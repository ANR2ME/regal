//
//  main.cpp
//  minimal_glut
//
//  Created by Cass Everitt on 2/1/12.
//  Copyright (c) 2012 n/a. All rights reserved.
//

#include <GL/Regal.h>

#ifdef __APPLE__
#include <GLUT/glut.h>
#else
#include <GL/RegalGLUT.h>
#endif

#include <GL/RegalGLU.h>

#include "render.h"

#include <cstdio>
#include <cstdlib>

static void myDisplay()
{
  display(true);
  glutSwapBuffers();
}

static void myTick(int dummy)
{
  glutPostRedisplay();
  glutTimerFunc( 16, myTick, 0 );
}

static void myKeyboard(unsigned char c, int x, int y)
{
  switch (c)
  {
    case 'q':
    case 27:  /* Esc key */
      exit(0);
      break;
  }
}

static void myOutput(GLenum stream, GLsizei length, const GLchar *message, GLvoid *context)
{
  static int line = 0;
  fprintf(stdout,"%6d | %s",++line,message);
  fflush(stdout);
}

static void myError(GLenum error)
{
  printf("dreamtorus error: %s\n",glErrorStringREGAL(error));
}

int main(int argc, const char *argv[])
{
  glutInitDisplayString("rgba>=8 depth double");
  glutInitWindowSize(500, 500);
  glutInit( &argc, (char **) argv);
  glutCreateWindow("dreamtorus");

  glLogMessageCallbackREGAL(myOutput);

  // Regal workaround for OSX GLUT

  #ifdef __APPLE__
  RegalMakeCurrent(CGLGetCurrentContext());
  #endif

  RegalSetErrorCallback(myError);

  // Exercise REGAL_extension_query extension

  if (glIsSupportedREGAL("GL_REGAL_extension_query"))
  {
    printf("GL_REGAL_extension_query is supported.\n");

    if (glIsSupportedREGAL("GL_EXT_debug_marker"))
      printf("GL_EXT_debug_marker is supported.\n");
    else
      printf("GL_EXT_debug_marker is not supported.\n");

    if (glIsSupportedREGAL("GL_EXT_framebuffer_object"))
      printf("GL_EXT_framebuffer_object is supported.\n");
    else
      printf("GL_EXT_framebuffer_object is not supported.\n");

    if (glIsSupportedREGAL("GL_EXT_direct_state_access"))
      printf("GL_EXT_direct_state_access is supported.\n");
    else
      printf("GL_EXT_direct_state_access is not supported.\n");

    if (glIsSupportedREGAL("GL_NV_path_rendering"))
      printf("GL_NV_path_rendering is supported.\n");
    else
      printf("GL_NV_path_rendering is not supported.\n");
  }

  glutTimerFunc(16, myTick, 0);
  glutDisplayFunc(myDisplay);
  glutReshapeFunc(reshape);
  glutKeyboardFunc(myKeyboard);
  glutMainLoop();
  return 0;
}
