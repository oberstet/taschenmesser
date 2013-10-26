# Taschenmesser

Taschenmesser is a toolbelt containing builders for [SCons](http://www.scons.org/). It helps you getting stuff done.

It contains builders for:

  - SVG optimization (Scour-based)
  - SVG2PNG conversion (Inkscape-based)
  - Amazon Web Service (S3 Delta Uploads etc)
  - Google Closure (JavaScript optimization)
  - File utils (GZip etc)

License: Apache 2.0

## Installation

### Python and SCons

Taschenmesser is written in [Python](http://www.python.org/) and comes as a plugin for [SCons](http://www.scons.org/). You'll need those for all uses.

### Taschenmesser

Install Taschenmesser

	easy_install -U taschenmesser

### Scour

For SVG optimization, you will need [Scour](https://github.com/oberstet/scour):

	easy_install -U scour

### Inkscape

For SVG-to-PNG conversion, you will need [Inkscape](http://inkscape.org/).

### Boto

For Amazon Web Service features, you will need [Boto](https://github.com/boto/boto):

	easy_install -U boto

## Examples

### SVG Optimization

Here is an example `SConstruct` makefile that produces optimized SVGs:


	SVG_FILES = ['myfigure.svg']
	
	IMG_SOURCE_DIR = "design"
	IMG_GEN_DIR    = "gen"

	import pkg_resources
	taschenmesser = pkg_resources.resource_filename('taschenmesser', '..')

	env = Environment(tools = ['default', 'taschenmesser'], toolpath = [taschenmesser])

	for svg in SVG_FILES:
	   svgOpt = env.Scour("%s/%s" % (IMG_GEN_DIR, svg),
	                      "%s/%s" % (IMG_SOURCE_DIR, svg))

You can then just do:

	scons

and you'll get optimized SVGs that work in most browsers.

To cleanup, do:

	scons -uc

### Other builders

Write me.