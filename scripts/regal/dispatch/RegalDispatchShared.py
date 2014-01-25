#!/usr/bin/python -B

from string import Template, upper, replace

from ApiCodeGen import paramsDefaultCode
from ApiCodeGen import paramsNameCode, typeCode

from RegalContextInfo import cond as condDefault

############################################################################

dispatchSourceTemplate = Template('''${AUTOGENERATED}
${LICENSE}

#include "pch.h" /* For MS precompiled header support */

#include "RegalUtil.h"

${IFDEF}REGAL_GLOBAL_BEGIN

#include <string>
using namespace std;

#include "RegalLog.h"
#include "RegalBreak.h"
#include "RegalPush.h"
#include "RegalToken.h"
#include "RegalHelper.h"
#include "RegalPrivate.h"
#include "RegalContext.h"
${LOCAL_INCLUDE}

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

using namespace ::REGAL_NAMESPACE_INTERNAL::Logging;
using namespace ::REGAL_NAMESPACE_INTERNAL::Token;

${LOCAL_CODE}

${API_DISPATCH_FUNC_DEFINE}

void InitDispatch${DISPATCH_NAME}( Layer *layer, Dispatch::GL &tbl )
{
  ${API_DISPATCH_FUNC_INIT}
}

${API_DISPATCH_GLOBAL_FUNC_INIT}

REGAL_NAMESPACE_END

${ENDIF}''')

############################################################################

emuProcsHeaderTemplate = Template('''${AUTOGENERATED}
${LICENSE}

#ifndef ${HEADER_NAME}
#define ${HEADER_NAME}

#include "RegalUtil.h"

${IFDEF}REGAL_GLOBAL_BEGIN

#include "RegalPrivate.h"
#include "RegalContext.h"
#include "RegalDispatch.h"
${LOCAL_INCLUDE}

REGAL_GLOBAL_END

REGAL_NAMESPACE_BEGIN

${LOCAL_CODE}

REGAL_NAMESPACE_END

${ENDIF}
#endif // ${HEADER_NAME}
''')


def apiDispatchFuncInitCode(apis, args, dispatchName, exclude=[], filter = lambda x : True, cond = None):

  if not cond:
    cond = condDefault

  categoryPrev = None
  code = ''

  for api in apis:

    code += '\n'
    if api.name in cond:
      code += '#if %s\n' % cond[api.name]

    for function in api.functions:

      if not function.needsContext:
        continue

      if not filter(function):
        continue

      if getattr(function,'regalOnly',False)==True:
        continue

      if function.name in exclude or function.category in exclude:
        continue

      name   = function.name
      params = paramsDefaultCode(function.parameters, True)
      callParams = paramsNameCode(function.parameters)
      rType  = typeCode(function.ret.type)
      category  = getattr(function, 'category', None)
      version   = getattr(function, 'version', None)

      if category:
        category = category.replace('_DEPRECATED', '')
      elif version:
        category = version.replace('.', '_')
        category = 'GL_VERSION_' + category

      # Close prev category block.
      if categoryPrev and not (category == categoryPrev):
        code += '\n'

      # Begin new category block.
      if category and not (category == categoryPrev):
        code += '  // %s\n\n' % category

      categoryPrev = category

      if dispatchName!=None:
        code += '  tbl.%s = MakeRegalProc( %s_%s, layer );\n' % ( name, dispatchName, name )
      else:
        code += '    tbl.%s = MakeRegalProc( %s, layer );\n' % ( name, name )

    if api.name in cond:
      code += '#endif // %s\n' % cond[api.name]
    code += '\n'

  # Close pending if block.
  if categoryPrev:
    code += '\n'

  return code

def apiDispatchGlobalFuncInitCode(apis, args, dispatchName, exclude=[], filter = lambda x : True, cond = None):

  if not cond:
    cond = condDefault

  categoryPrev = None
  code = '''
void InitDispatch%s%s( Layer * layer, Dispatch::Global &tbl)
{
'''%(dispatchName[0:1].upper(),dispatchName[1:])

  for api in apis:

    code += '\n'
    if api.name in cond:
      code += '#if %s\n' % cond[api.name]

    for function in api.functions:

      if function.needsContext:
        continue

      if not filter(function):
        continue

      if getattr(function,'regalOnly',False)==True:
        continue

      if function.name in exclude or function.category in exclude:
        continue

      name   = function.name
      params = paramsDefaultCode(function.parameters, True)
      callParams = paramsNameCode(function.parameters)
      rType  = typeCode(function.ret.type)
      category  = getattr(function, 'category', None)
      version   = getattr(function, 'version', None)

      if category:
        category = category.replace('_DEPRECATED', '')
      elif version:
        category = version.replace('.', '_')
        category = 'GL_VERSION_' + category

      # Close prev category block.
      if categoryPrev and not (category == categoryPrev):
        code += '\n'

      # Begin new category block.
      if category and not (category == categoryPrev):
        code += '  // %s\n\n' % category

      categoryPrev = category

      if dispatchName!=None:
        code += '  tbl.%s = MakeRegalProc(%s_%s, layer);\n' % ( name, dispatchName, name )
      else:
        code += '    tbl.%s = MakeRegalProc(%s, layer);\n' % ( name, name )

    if api.name in cond:
      code += '#endif // %s\n' % cond[api.name]
    code += '\n'

  # Close pending if block.
  if categoryPrev:
    code += '\n'

  code += '}\n'

  return code

