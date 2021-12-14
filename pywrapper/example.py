#
# this is pysdl2 based testing skeleton. i ditched pygame because it's not as cross-platform
# as i'd like (mainly the ridiculous macosx install situation.. X11/XQuartz dependency..?)
#

import logging
logg = logging.getLogger(__name__)
if __name__=="__main__":
    logging.basicConfig(level=logging.NOTSET, format="%(asctime)s %(name)s %(levelname)-5s: %(message)s")

import sys
import time
import math

from sdl2 import *
from OpenGL.GL import *
import ctypes

import gltext
#import gltext_pyopenglversion # uncomment if you want to test the python version of gltext lib.


class FpsCounter:
    def __init__(self, update_interval_seconds=0.5):
        """ read self.fps for output """
        self.fps = 0.
        self.interval = update_interval_seconds
        self._counter = 0.
        self._age     = 0.
        self._last_output_age = 0.

    def tick(self, dt):
        self._age     += dt
        self._counter += 1.
        if self._age > self.interval:
            self.fps = self._counter / self._age
            self._age     = 0.
            self._counter = 0.


class Test:
    def __init__(self):
        self.w = 800
        self.h = 600

        self.fpscounter = FpsCounter()
        self.gltext = None

    def run(self):
        if SDL_Init(SDL_INIT_VIDEO) != 0:
            logg.error(SDL_GetError())
            return -1

        window = SDL_CreateWindow(b"gltext test O_o", SDL_WINDOWPOS_UNDEFINED,
                                  SDL_WINDOWPOS_UNDEFINED, self.w, self.h,
                                  SDL_WINDOW_OPENGL | SDL_WINDOW_ALLOW_HIGHDPI | SDL_WINDOW_RESIZABLE)
        if not window:
            logg.error(SDL_GetError())
            return -1

        context = SDL_GL_CreateContext(window)

        glClearColor(0., 0., 0., 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if SDL_GL_SetSwapInterval(-1):
            logg.error(SDL_GetError())
            if SDL_GL_SetSwapInterval(1):
                logg.error("SDL_GL_SetSwapInterval: %s", SDL_GetError())
                logg.error("vsync failed completely. will munch cpu for lunch.")

        #Drawable size
        drawable_w = ctypes.c_int()
        drawable_h = ctypes.c_int()

        SDL_GL_GetDrawableSize(window, ctypes.byref(drawable_w), ctypes.byref(drawable_h))
        self.d_w = drawable_w.value
        self.d_h = drawable_h.value

        self._init_gl()
        self.gltext = gltext.GLText(b"../data/font_proggy_opti_small.txt")
        self.gltext.init()

        # init done. start the mainloop!

        last_t = time.time()

        event = SDL_Event()
        running = True
        while running:
            while SDL_PollEvent(ctypes.byref(event)) != 0:
                if event.type == SDL_QUIT:
                    running = False

                if event.type == SDL_KEYDOWN:
                    if event.key.keysym.scancode == SDL_SCANCODE_ESCAPE:
                        running = False

                if event.type == SDL_WINDOWEVENT:
                    if event.window.event == SDL_WINDOWEVENT_SIZE_CHANGED:
                        SDL_GL_GetDrawableSize(window, ctypes.byref(drawable_w), ctypes.byref(drawable_h))
                        glViewport(0, 0, drawable_w.value, drawable_h.value)

            t = time.time()
            self._render_frame(t - last_t)
            last_t = t

            #glFinish()
            SDL_GL_SwapWindow(window)
            #SDL_Delay(10)

        SDL_GL_DeleteContext(context)
        SDL_DestroyWindow(window)
        SDL_Quit()

    def _render_frame(self, dt):
        self.fpscounter.tick(dt)

        glClearColor(0., 0., 0., 1.)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        w, h = self.w, self.h
        tx = self.gltext

        t = time.time()
        for i in range(200):
            tx.drawmm(b"day %03i" % i, w/2. + 250*math.sin(t*.1+i*0.1)*math.sin(t*.245+i*.01), h/2. + 180*math.cos(t*.1+i*0.01), fgcolor=(1., 1.0, 1.0, 1.0), bgcolor=(i/200., 0.4, 0.5, 1.))

        tx.drawtl(b"top-left",     0, 0, fgcolor=(1., 1., 1., 1.0), bgcolor=(0., 0., 0., 0.), z=1000.)
        tx.drawbl(b"bottom-left",  0, h)
        tx.drawtr(b"top-right",    w, 0)
        tx.drawbr(b"bottom-right", w, h)

        tx.drawmm(b"middle", w / 2, h / 2, bgcolor=(.3, .4, .5, .5))

        tx.drawmm(b"fps: %i" % (self.fpscounter.fps), w / 2, h / 2 + tx.height, fgcolor=(1.0, 0.7, 0.7, 1.0), bgcolor=(0., 0., 0., 0.))

    def _init_gl(self):
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_FOG)
        glDisable(GL_DITHER)
        glDisable(GL_LIGHTING)
        glShadeModel(GL_FLAT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glDisable(GL_LINE_STIPPLE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        z_near, z_far = 101., 100000.
        glViewport(0, 0, self.d_w, self.d_h)
        glOrtho(0., self.w, self.h, 0., z_near, z_far)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glScale(1., 1., -1.)


if __name__=="__main__":
    w = Test()
    sys.exit(w.run())
