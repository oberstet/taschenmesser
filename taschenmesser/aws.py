###############################################################################
##
##  Copyright 2013 (C) Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = ['exists', 'generate']


import hashlib


def exists(env):
   try:
      import boto
      return True
   except:
      print "Taschenmesser: Boto library missing. Upload to Amazon S3 won't be available."
      return False



def generate(env):
   from SCons.Builder import Builder

   import os, sys, hashlib, gzip, posixpath
   import subprocess

   from boto.s3.connection import S3Connection
   from boto.s3.key import Key


   def s3_uploader(target, source, env):
      """
      SCons builder for Amazon S3 upload.
      """

      def s3_upload_percent_cb(complete, total):
         if total > 0:
            sys.stdout.write("%d %%\n" % round(100. * float(complete) / float(total)))
            sys.stdout.flush()

      ## the bucket, bucket prefix and object ACLs come from env
      ##
      s3_bucket_name = env['S3_BUCKET']
      s3_object_acl = env.get('S3_OBJECT_ACL', 'public-read')

      s3_bucket_prefix = env.get('S3_BUCKET_PREFIX', '')
      s3_relpath = env.get('S3_RELPATH', None)


      def rpath(o):
         """
         Convert scons source file object to remote S3 URL path.
         """
         if s3_relpath:
            return (s3_bucket_prefix + os.path.relpath(o.path, s3_relpath)).replace('\\', '/')
         else:
            return (s3_bucket_prefix + o.name).replace('\\', '/')


      ## S3 connection and bucket to upload to
      ##
      s3 = S3Connection()
      bucket = s3.get_bucket(s3_bucket_name)

      ## compute MD5s of artifacts to upload
      ##
      checksums = {}
      for s in source:
         key = Key(s.path)
         md5 = key.compute_md5(open(s.path, "rb"))[0]
         checksums[s.path] = md5

      ## determine stuff we need to upload
      ##
      uploads = []
      for s in source:
         key = bucket.lookup(rpath(s))
         if not key or key.etag.replace('"', '') != checksums[s.path]:
            uploads.append(s)
         else:
            print "%s unchanged versus S3" % s.name

      ## actually upload new or changed stuff
      ##
      for u in uploads:
         print "Uploading '%s' to S3 at '%s' .." % (u.path, rpath(u))
         key = Key(bucket, rpath(u))

         ## Do special stuff for "*.jgz", etc. Note that "set_metadata"
         ## must be set before uploading!
         ##
         ext = os.path.splitext(u.name)[1].lower()
         if ext == '.jgz':
            key.set_metadata('Content-Type', 'application/x-javascript')
            key.set_metadata('Content-Encoding', 'gzip')
         elif ext == '.atom':
            key.set_metadata('Content-Type', 'application/atom+xml')

         key.set_contents_from_filename(u.path, cb = s3_upload_percent_cb, num_cb = 100)
         key.set_acl(s3_object_acl)

      ## revisit uploaded stuff and get MD5s
      ##
      checksumsS3 = {}
      for s in source:
         key = bucket.lookup(rpath(s))
         md5 = key.etag.replace('"', '')
         checksumsS3[s.name] = md5
      checksumsS3String = ''.join(["MD5 (%s) = %s\n" % c for c in checksumsS3.items()])

      ## target produced is checksums as they exist on S3
      ##
      f = open(target[0].path, "wb")
      f.write(checksumsS3String)
      f.close()


   def checksumsMD5(target, source, env):
      """
      SCons builder for computing a MD5 fingerprint file for artifacts.
      """
      checksums = {}
      for s in source:
         key = Key(s.name)
         md5 = key.compute_md5(open(s.path, "rb"))[0]
         checksums[s.name] = md5

      ## MD5 (autobahn.js) = 9f26d4774ce6ebafd32e75b68b22a526
      ##
      checksumsString = ''.join(["MD5 (%s) = %s\n" % c for c in checksums.items()])

      f = open(target[0].path, 'wb')
      f.write(checksumsString)
      f.close()


   def checksumsSHA1(target, source, env):
      """
      SCons builder for computing a SHA1 fingerprint file for artifacts.
      """
      checksums = {}
      for s in source:
         m = hashlib.sha1()
         m.update(open(s.path, "rb").read())
         fp = m.hexdigest()
         checksums[s.name] = fp

      ## SHA1 (autobahn.js) = 82e4e4961b8c68189f57a1c4b57b3953d5234850
      ##
      checksumsString = ''.join(["SHA1 (%s) = %s\n" % c for c in checksums.items()])

      f = open(target[0].path, 'wb')
      f.write(checksumsString)
      f.close()


   def checksumsSHA256(target, source, env):
      """
      SCons builder for computing a SHA256 fingerprint file for artifacts.
      """
      checksums = {}
      for s in source:
         m = hashlib.sha256()
         m.update(open(s.path, "rb").read())
         fp = m.hexdigest()
         checksums[s.name] = fp

      ## SHA256 (autobahn.js) = be266f59ff09214f4afe610c0c15abc10b86e96e82e943749efacfb7f8d72dd0
      ##
      checksumsString = ''.join(["SHA256 (%s) = %s\n" % c for c in checksums.items()])

      f = open(target[0].path, 'wb')
      f.write(checksumsString)
      f.close()


   env.Append(BUILDERS = {'S3': Builder(action = s3_uploader),
                          'MD5': Builder(action = checksumsMD5),
                          'SHA1': Builder(action = checksumsSHA1),
                          'SHA256': Builder(action = checksumsSHA256)})
