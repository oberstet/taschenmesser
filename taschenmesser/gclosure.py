##############################################################################
#
#  Copyright (c) Crossbar.io Technologies GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
##############################################################################

from __future__ import absolute_import

import os, subprocess
from SCons.Builder import Builder

__all__ = ['exists', 'generate']


def exists(env):
   if 'JAVA_HOME' in os.environ:
      env['JAVA_HOME'] = os.environ['JAVA_HOME']
   else:
      print("Taschenmesser: Google Closure Compiler won't be available (no JAVA_HOME set)")
      return False

   if 'JS_COMPILER' in os.environ:
      env['JS_COMPILER'] = os.environ['JS_COMPILER']
   else:
      print("Taschenmesser: Google Closure Compiler won't be available (JS_COMPILER environment variable must be set and point to full path of 'compiler.jar')")
      return False

   return True



def generate(env):

   def js_builder(target, source, env):
      """
      SCons builder for Google Closure.
      """
      clevel = env.get('JS_COMPILATION_LEVEL', None)
      coutlang = env.get('JS_OUTPUT_LANG', None)
      strict = env.get("JS_STRICT_MODE", None)

      if clevel == 'NONE':
         outfile = str(target[0])
         of = open(outfile, 'w')
         for file in source:
            of.write(open(str(file)).read())
            of.write("\n")
         of.close()

      else:
         cmd = []
         #cmd.append(os.path.join(env['JAVA_HOME'], 'bin', 'java'))
         cmd.append('java')

         cmd.extend(['-jar', env['JS_COMPILER']])

         if clevel in ['WHITESPACE_ONLY', 'SIMPLE_OPTIMIZATIONS', 'ADVANCED_OPTIMIZATIONS']:
            cmd.extend(['--compilation_level', clevel])

         # see https://github.com/google/closure-compiler/wiki/Flags-and-Options#basic-usage
         out_levels = [
            "ECMASCRIPT3", "ECMASCRIPT5", "ECMASCRIPT_2015", "ECMASCRIPT_2016", "ECMASCRIPT_2017",
            "ECMASCRIPT_2018", "ECMASCRIPT_2019", "ECMASCRIPT_2020", "ECMASCRIPT_2021", "STABLE",
            "ECMASCRIPT_NEXT"
         ]

         if coutlang in out_levels:
            cmd.extend(['--language_out', coutlang])

         if env.get('JS_DEFINES'):
            for define in env['JS_DEFINES']:
               cmd.append('--define="%s=%s"' % (define, env['JS_DEFINES'][define]))

         # allow to disable strict mode to workaround issues like:
         # https://github.com/google/closure-compiler/issues/3014
         if strict is not None and strict in ["0", "1"]:
            cmd.extend(['--strict_mode_input', "true" if strict == 1 else "false"])

         for file in source:
            cmd.extend(["--js", str(file)])

         cmd.extend(["--js_output_file", str(target[0])])

         #cmd.append("--warning_level=VERBOSE")
         #cmd.append("--jscomp_warning=missingProperties")
         #cmd.append("--jscomp_warning=checkTypes")

         print(' '.join(cmd))
         subprocess.call(cmd)

   env.Append(BUILDERS = {'JavaScript': Builder(action = js_builder)})
