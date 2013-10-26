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

For SVG-to-PNG conversion, you will need [Inkscape](http://inkscape.org/). Make sure the Inkscape executable is on your `PATH`.

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

### SVGs, PNGs and GZipped versions

Here is a more complete example `SConstruct` that show how to produce:

 * Optimized SVGs
 * PNGs from those
 * GZipped versions of all

everything produced via a single command.

	SVG_FILES = ['myfigure.svg', 'awesome_shit1.svg', 'awesome_shit2.svg']
	
	IMG_SOURCE_DIR = "design"
	IMG_GEN_DIR    = "gen"

	import pkg_resources
	taschenmesser = pkg_resources.resource_filename('taschenmesser', '..')

	env = Environment(tools = ['default', 'taschenmesser'], toolpath = [taschenmesser])

	for svg in SVG_FILES:
	   svgOpt = env.Scour("%s/%s" % (IMG_GEN_DIR, svg),
	                      "%s/%s" % (IMG_SOURCE_DIR, svg),
	                      SCOUR_OPTIONS = {'enable_viewboxing': True})

	   env.GZip("%s.gz" % svgOpt[0], svgOpt)
	
	   png = env.Svg2Png("%s.png" % os.path.splitext(str(svgOpt[0]))[0],
                         svgOpt,
                         SVG2PNG_OPTIONS = {})

	   env.GZip("%s.gz" % png[0], png)

### Amazon S3

Write me.

### Google Closure

Write me.
