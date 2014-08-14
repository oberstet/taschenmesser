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

import os

from SCons.Script import *


def exists(env):
   try:
      import hashlib, gzip
      return True
   except:
      print "Taschenmesser: hashlib or gzip missing"
      return False



def generate(env):
   from SCons.Builder import Builder
   import hashlib, gzip

   def gzipper(target, source, env):
      if len(source) > 1:
         raise Exception("cannot GZip multiple files")
      f_in = open(source[0].path, 'rb')

      ## make sure we don't embed a modification time so we get
      ## content stable, repeatable packaging
      f_out = gzip.GzipFile(target[0].path, 'wb', mtime = 0)
      #f_out = gzip.open(target[0].path, 'wb')

      f_out.writelines(f_in)
      f_out.close()
      f_in.close()


   env.Append(BUILDERS = {'GZip': Builder(action = gzipper)})


   import subprocess

   def get_git_latest_commit(gitdir = None):
      """
      Get git info line on latest commit.

      E.g.: Jay Martin (Wed Aug 13 07:46:39 2014 -0700): Updated Router Realms (markdown)

      Usage: env['COMMIT'] = env.GetLatestCommit()
      """
      gitdir = gitdir or '.git'
      cmd = 'git --git-dir="{}" log -1 --pretty=format:"%an (%ad): %s"'.format(gitdir)
      output = subprocess.check_output(cmd, shell = True).strip()
      return output

   env.GetLatestCommit = get_git_latest_commit


   def get_git_revision():
      """
      Get git revision stamp of HEAD.

      Usage: env['REVISION'] = env.GetRevision()
      """
      return subprocess.check_output("git rev-parse HEAD", shell = True).strip()

   env.GetRevision = get_git_revision


   def version_stamp(target, source, env):
      """
      Replace __VERSION__ and __REVISION__ in file.
      """
      content = open(source[0].path).read()
      if len(source) > 1 and source[1]:
         version = open(source[1].path).read().strip()
         content = content.replace('__VERSION__', version)
      if len(source) > 2 and source[2]:
         revision = open(source[2].path).read().strip()
         content = content.replace('__REVISION__', revision)
      fd = open(target[0].path, 'w')
      fd.write(content)
      fd.close()

   env.Append(BUILDERS = {'VersionStamp': Builder(action = version_stamp)})


   def _getfiles(rdir):
      res = []
      for root, subdirs, files in os.walk(rdir):
         for file in files:
            f = os.path.join(root, file)
            res.append(f)
         for sdir in subdirs:
            res.extend(_getfiles(sdir))
      return res

   def findfiles(paths, recurse = True, patterns = None):
      res = []
      if not type(paths) == list:
         paths = [paths]
      for path in paths:
         if os.path.isfile(path):
            res.append(path)
         elif os.path.isdir(path) and recurse:
            res.extend(_getfiles(path))
         else:
            pass
      return res

   def copyfiles(targetdir, files):
      res = []
      for f in files:
         #fp = os.path.join('build', targetdir,  f)
         fp = os.path.join(targetdir,  f)
         res.append(Command(fp, f, Copy("$TARGET", "$SOURCE")))
      return res

   env.FindFiles = findfiles
   env.CopyFiles = copyfiles
