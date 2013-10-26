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


def exists(env):
   try:
      import boto
      return True
   except:
      print "Taschenmesser: Boto library missing. Upload to Amazon S3 won't be available."
      return False



def generate(env):
   from SCons.Builder import Builder

   import os, sys, hashlib, gzip
   import subprocess

   from boto.s3.connection import S3Connection
   from boto.s3.key import Key

   def s3_uploader(target, source, env):
      """
      SCons builder for Amazon S3 upload.
      """
      ## S3 connection and bucket to upload to
      ##
      s3 = S3Connection()
      bucket = s3.get_bucket("autobahn")

      ## compute MD5s of artifacts to upload
      ##
      checksums = {}
      for s in source:
         key = Key(s.name)
         md5 = key.compute_md5(open(s.path, "rb"))[0]
         checksums[s.name] = md5

      ## determine stuff we need to upload
      ##
      uploads = []
      for s in source:
         key = bucket.lookup("js/%s" % s.name)
         if not key or key.etag.replace('"', '') != checksums[s.name]:
            uploads.append(s)
         else:
            print "%s unchanged versus S3" % s.name

      ## actually upload new or changed stuff
      ##
      for u in uploads:
         print "Uploading %s to S3 .." % u.name
         key = Key(bucket, "js/%s" % u.name)
         ##
         ## Do special stuff for "*.jgz". Note that "set_metadata"
         ## must be set before uploading!
         ##
         if os.path.splitext(u.name)[1].lower() == ".jgz":
            ## override default chosen by S3 ..
            key.set_metadata('Content-Type', 'application/x-javascript')
            key.set_metadata('Content-Encoding', 'gzip')
         key.set_contents_from_filename(u.path)
         key.set_acl('public-read')

      ## revisit uploaded stuff and get MD5s
      ##
      checksumsS3 = {}
      for s in source:
         key = bucket.lookup("js/%s" % s.name)
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
      SCons builder for computing a fingerprint file for artifacts.
      """
      checksums = {}
      for s in source:
         key = Key(s.name)
         md5 = key.compute_md5(open(s.path, "rb"))[0]
         checksums[s.name] = md5

      ## MD5 (autobahn.js) = d1ff7ad2c5c4cf0d652566cbc78476ea
      ##
      checksumsString = ''.join(["MD5 (%s) = %s\n" % c for c in checksums.items()])

      f = open(target[0].path, 'wb')
      f.write(checksumsString)
      f.close()


   env.Append(BUILDERS = {'S3': Builder(action = s3_uploader),
                          'MD5': Builder(action = checksumsMD5)})
