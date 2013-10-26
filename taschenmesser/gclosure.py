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
   import os

   if os.environ.has_key('JAVA_HOME'):
      env['JAVA_HOME'] = os.environ['JAVA_HOME']
   else:
      print "Need to have a Java Run-time - please set JAVA_HOME ennvironment variable."
      return False

   if os.environ.has_key('JS_COMPILER'):
      env['JS_COMPILER'] = os.environ['JS_COMPILER']
   else:
      print "Need path to Google Closure Compiler JAR (compiler.jar) in JS_COMPILER environment variable."
      return False

   return True



def generate(env):
   from SCons.Builder import Builder
   import os, subprocess

   def js_builder(target, source, env):
      """
      SCons builder for Google Closure.
      """
      if env['JS_COMPILATION_LEVEL'] == 'NONE':
         outfile = str(target[0])
         of = open(outfile, 'w')
         for file in source:
            of.write(open(str(file)).read())
            of.write("\n")
         of.close()

      else:
         cmd = []
         cmd.append(os.path.join(env['JAVA_HOME'], 'bin', 'java'))

         cmd.extend(['-jar', env['JS_COMPILER']])

         for define in env['JS_DEFINES']:
            cmd.append('--define="%s=%s"' % (define, env['JS_DEFINES'][define]))

         for file in source:
            cmd.extend(["--js", str(file)])

         cmd.extend(["--js_output_file", str(target[0])])

         #cmd.append("--warning_level=VERBOSE")
         #cmd.append("--jscomp_warning=missingProperties")
         #cmd.append("--jscomp_warning=checkTypes")

         print ' '.join(cmd)
         subprocess.call(cmd)

   env.Append(BUILDERS = {'JavaScript': Builder(action = js_builder)})
