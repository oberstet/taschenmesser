###############################################################################
##
##  Copyright (C) 2013-2015 Tavendo GmbH
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

import re
import os

# The following monkey patch is for buckets containing periods
# and due to the following
# https://github.com/boto/boto/issues/2836

# disable hostname verification altogether
# import ssl
# if hasattr(ssl, '_create_unverified_context'):
#    ssl._create_default_https_context = ssl._create_unverified_context

# more specific monkey patch:
try:
   import ssl
except:
   print("Taschenmesser: no SSL available - secure upload to S3 won't be available")
else:
   if hasattr(ssl, 'match_hostname'):
      _old_match_hostname = ssl.match_hostname

      # crossbario.com.s3.amazonaws.com => s3.amazonaws.com
      pattern1 = re.compile(r'^(.*).s3.amazonaws.com$')

      # crossbario.com.s3.eu-central-1.amazonaws.com => s3.eu-central-1.amazonaws.com
      pattern2 = re.compile(r'^(.*).s3.(.*).amazonaws.com$')

      def _new_match_hostname(cert, hostname):
         match1 = pattern1.match(hostname)
         if match1:
            hostname = 's3.amazonaws.com'
         else:
            match2 = pattern2.match(hostname)
            if match2:
               _, region = match2.groups()
               hostname = 's3.{}.amazonaws.com'.format(region)

         return _old_match_hostname(cert, hostname)

      ssl.match_hostname = _new_match_hostname

import hashlib

import mimetypes
mimetypes.add_type('application/atom+xml', '.atom')
mimetypes.add_type('text/javascript', '.jgz')
mimetypes.add_type('image/svg+xml', '.svg')

## any additional file extensions that signal Gzip encoding when not
## explicitly found via Python's mimetypes module
##
GZIP_ENCODING_FILE_EXTS = ['.gz', '.jgz']

import email
import time
from datetime import datetime, timedelta


def exists(env):
   try:
      import boto
      return True
   except:
      print("Taschenmesser: Boto library missing. Upload to Amazon S3 won't be available.")
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
      s3_maxages = env.get('S3_MAXAGES', None) or {}

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
      s3 = None
      bucket = None
      try:
         s3 = S3Connection()
         bucket = s3.get_bucket(s3_bucket_name)
      except:
         # this an ugly, half-baked patch to make FFM region work
         # (as well as possibly other regions)
         # http://stackoverflow.com/a/29391782/884770
         # https://github.com/boto/boto/issues/2916
         # https://github.com/danilop/yas3fs/issues/101
         # https://github.com/boto/boto/issues/2741
         os.environ['S3_USE_SIGV4'] = 'True'
         s3 = S3Connection(host='s3.eu-central-1.amazonaws.com')
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
            print("{0} unchanged versus S3".format(rpath(s)))

      ## actually upload new or changed stuff
      ##
      for u in uploads:
         print("Uploading '{0}' to S3 at '{1}' ..".format(u.path, rpath(u)))
         key = Key(bucket, rpath(u))

         file_ext = os.path.splitext(u.name)[1].lower()
         content_type, content_encoding = mimetypes.guess_type(u.name)

         ## Note that "set_metadata" must be set before uploading!
         ##
         if content_type:
            key.set_metadata('Content-Type', content_type)
         if content_encoding:
            key.set_metadata('Content-Encoding', content_encoding)
         elif file_ext in GZIP_ENCODING_FILE_EXTS:
            key.set_metadata('Content-Encoding', 'gzip')

         def set_maxage(key, days):
            ## HTTP 1.0
            expires = '%s GMT' % (email.Utils.formatdate(time.mktime((datetime.now() + timedelta(days = days)).timetuple())))
            key.set_metadata('Expires', expires)

            ## HTTP 1.1
            max_age = 'max-age=%d, public' % (3600 * 24 * days)
            key.set_metadata('Cache-Control', max_age)

         if file_ext in s3_maxages:
            set_maxage(key, s3_maxages[file_ext])

         if content_type in s3_maxages:
            set_maxage(key, s3_maxages[content_type])

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


   def s3_dir_uploader(buildir, localdir, bucket, prefix, maxages = None):
      """
      Uploads a whole directory tree to S3.

      :param builddir: Directory where to put file upload checksum files.
      :type builddir: str
      :param localdir: The local directory to upload from.
      :type localdir: str
      :param bucket: The Amazon S3 bucket to upload to.
      :type bucket: str
      :param prefix: The prefix within the S3 bucket to upload to (must end with a slash!)
      :type prefix: str
      """
      if prefix and prefix[-1] != '/':
            prefix += '/'

      uploaded = []

      for root, dirnames, filenames in os.walk(localdir):
         for filename in filenames:
            source = os.path.join(root, filename)
            target = os.path.join(buildir, source)
            uploaded.append(env.S3('{}.s3'.format(target),
                            source,
                            S3_RELPATH = localdir,
                            S3_BUCKET = bucket,
                            S3_BUCKET_PREFIX = prefix,
                            S3_OBJECT_ACL = 'public-read',
                            S3_MAXAGES = maxages))

      return uploaded


   env.Append(BUILDERS = {'S3': Builder(action = s3_uploader),
                          'MD5': Builder(action = checksumsMD5),
                          'SHA1': Builder(action = checksumsSHA1),
                          'SHA256': Builder(action = checksumsSHA256)})

   env.s3_dir_uploader = s3_dir_uploader
