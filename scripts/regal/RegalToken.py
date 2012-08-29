#!/usr/bin/python -B

from string import Template, upper, replace

from ApiUtil import outputCode
from ApiUtil import toLong
from ApiUtil import hexValue

tokenSourceTemplate = Template( '''${AUTOGENERATED}
${LICENSE}

#include "pch.h" /* For MS precompiled header support */

#include "RegalUtil.h"

REGAL_GLOBAL_BEGIN

#include "RegalPrivate.h"
#include "RegalToken.h"

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

namespace Token {

  const char * GLbooleanToString(GLboolean v)
  {
    return v==GL_FALSE ? "GL_FALSE" : "GL_TRUE";
  }

  const char * internalFormatToString(GLint v)
  {
    const char *integer[5] = { "", "1", "2", "3", "4" };
    return 1<=v && v<=4 ? integer[v] : GLenumToString(v);
  }

${CODE}

}

REGAL_NAMESPACE_END

''')

def generateTokenSource(apis, args):

  code = []

  code.append('  const char * GLenumToString( GLenum e ) {')
  code.append('    switch( e ) {')

  for i in apis:
    if i.name != 'gl':
      continue
    e = {}
    for j in i.enums:
      if j.name != 'defines':
        continue
      for k in j.enumerants:
        value = toLong(k.value)
        if value != None:
          if not value in e:
            e[value] = set()
          e[value].add(k.name)

    e = sorted([ (i,sorted(list(e[i]))) for i in e.iterkeys() ])

    e = [ i for i in e if i[0] < 0xfffffffff ]

    # Filter out extension duplicates

    u = e
    for i in ['_ARB','_EXT','_NV','_ATI','_PGI','_OES','_IBM','_SUN','_SGI','_SGIX','_SGIS','_APPLE']:
      u = [ (j[0], [ k for k in j[1] if not k.endswith(i)  ]) for j in u ]

    # Filter out _BIT duplicates

    for i in ['_BIT','_BITS']:
      u = [ (j[0], [ k for k in j[1] if not k.endswith(i)  ]) for j in u ]

    u = [ (i[0], [ j for j in i[1] if not j.startswith('GL_KTX_') ]) for i in u  ]

    # Form tuple of value, filtered names, all names, per GLenum

    e = [ (e[i][0], u[i][1], e[i][1]) for i in xrange(len(e)) ]

    for i in e:
      value = i[0]
      if len(i[1]):
        name = i[1][0]
      else:
        name = i[2][0]

      if value==0:
        name = 'GL_ZERO'
      if value==1:
        name = 'GL_ONE'

      code.append('      case %s: return "%s";'%(hexValue(value,'0x%08x'),name))

  code.append('      default: break;')
  code.append('    }')
  code.append('  return "unknown_gl_enum";')
  code.append('  }')

  # GLerrorToString

  code.append('')
  code.append('  const char * GLerrorToString( GLenum e ) {')
  code.append('    switch( e ) {')
  for i in apis:
    if i.name != 'gl':
      continue
    for j in i.enums:
      if j.name != 'defines':
        continue
      for k in j.enumerants:
        if getattr(k,'gluErrorString',None):
          code.append('      case %s: return "%s";'%(k.name,k.gluErrorString))
  code.append('      default: break;')
  code.append('    }')
  code.append('  return NULL;')
  code.append('  }')

  # GLX_VERSION

  code.append('')
  code.append('#if REGAL_SYS_GLX')
  code.append('  const char * GLXenumToString(int v) {')
  code.append('    switch( v ) {')

  for i in apis:
    if i.name != 'glx':
      continue
    e = {}
    for j in i.enums:
      if j.name != 'defines':
        continue
      for k in j.enumerants:
        value = toLong(k.value)
        if value != None:
          if not value in e:
            e[value] = set()
          e[value].add(k.name)

    e = sorted([ (i,sorted(list(e[i]))) for i in e.iterkeys() ])

    e = [ i for i in e if i[0] < 0xfffffffff ]

    # Filter out extension duplicates

    u = e
    for i in ['_ARB','_EXT','_NV','_ATI','_PGI','_OES','_IBM','_SUN','_SGI','_SGIX','_SGIS','_APPLE']:
      u = [ (j[0], [ k for k in j[1] if not k.endswith(i)  ]) for j in u ]

    # Filter out _BIT duplicates

    for i in ['_BIT','_BITS']:
      u = [ (j[0], [ k for k in j[1] if not k.endswith(i)  ]) for j in u ]

    u = [ (i[0], [ j for j in i[1] if not j.startswith('GL_KTX_') ]) for i in u  ]

    # Form tuple of value, filtered names, all names, per GLenum

    e = [ (e[i][0], u[i][1], e[i][1]) for i in xrange(len(e)) ]

    for i in e:
      value = i[0]
      if len(i[1]):
        name = i[1][0]
      else:
        name = i[2][0]

      code.append('      case %s: return "%s";'%(hexValue(value,'0x%08x'),name))

  code.append('      default: break;')
  code.append('    }')
  code.append('    return "unknown_glx_enum";')
  code.append('  }')
  code.append('#endif // REGAL_SYS_GLX')

  substitute = {}
  substitute['LICENSE']       = args.license
  substitute['AUTOGENERATED'] = args.generated
  substitute['COPYRIGHT']     = args.copyright
  substitute['CODE']          = '\n'.join(code)
  outputCode( '%s/RegalToken.cpp' % args.outdir, tokenSourceTemplate.substitute(substitute))

##############################################################################################

tokenHeaderTemplate = Template( '''${AUTOGENERATED}
${LICENSE}

#ifndef __${HEADER_NAME}_H__
#define __${HEADER_NAME}_H__

#include "RegalUtil.h"

REGAL_GLOBAL_BEGIN

#include <GL/Regal.h>

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

namespace Token {

  const char * GLenumToString        (GLenum    v);
  const char * GLerrorToString       (GLenum    v); // gluErrorString
  const char * GLbooleanToString     (GLboolean v);
  const char * internalFormatToString(GLint     v);

  #if REGAL_SYS_GLX
  const char * GLXenumToString       (int       v);
  #endif

  inline const char *toString(const GLenum    v) { return GLenumToString(v);    }
  inline const char *toString(const GLboolean v) { return GLbooleanToString(v); }
}

REGAL_NAMESPACE_END

#endif
''')

def generateTokenHeader(apis, args):

  substitute = {}
  substitute['LICENSE']       = args.license
  substitute['AUTOGENERATED'] = args.generated
  substitute['COPYRIGHT']     = args.copyright
  substitute['HEADER_NAME']   = "REGAL_TOKEN"
  outputCode( '%s/RegalToken.h' % args.outdir, tokenHeaderTemplate.substitute(substitute))