import numpy as np
from OpenGL import GL as gl


class ImageTexture(object):
    def __init__(self):
        self._id = None
        self._extend = (0, 0)
        self._internal_fmt = None

    def _reset(self):
        # deallocate
        if self._id is not None:
            gl.glDeleteTextures([self._id])

        self._id = None
        self._extend = (0, 0)
        self._internal_fmt = None

    @property
    def id(self):
        return 0 if self._id is None else int(self._id)
    
    @property
    def extend(self):
        return self._extend

    @property
    def width(self):
        return self._extend[0]

    @property
    def height(self):
        return self._extend[1]
    
    def empty(self):
        return self._id is None
    
    def build(self, img: np.ndarray, is_bgr=False):
        assert img.ndim == 3
        assert img.dtype == np.uint8
        h, w = img.shape[:2]
        self._extend = (w, h)
        # ? check resolution
        assert w % 2 == 0 and h % 2 == 0, "Given image {} should have even extend!".format((w, h))
        # get format
        self._internal_fmt = self._guess_internal_fmt(img)
        pix_fmt = self._guess_pix_fmt(img, is_bgr)
        # generate
        self._id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, self._internal_fmt,
                        w, h, 0, pix_fmt,
                        gl.GL_UNSIGNED_BYTE, img)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    
    def update(self, img: np.ndarray, pos = None, size = None, is_bgr=False):
        assert img.ndim == 3
        assert img.dtype == np.uint8
        if self.empty():
            return self.build(img, is_bgr=is_bgr)

        w0, h0 = self._extend
        h1, w1 = img.shape[:2]
        if pos is None: pos = (0, 0)
        if size is None: size = self._extend
        # check fmt
        assert self._internal_fmt == self._guess_internal_fmt(img)
        pix_fmt = self._guess_pix_fmt(img, is_bgr)
        # check size
        assert size[0] <= w1
        assert size[1] <= h1
        assert pos[0] + size[0] <= w0
        assert pos[1] + size[1] <= h0
        # update
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._id)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0,
                           pos[0], pos[1], size[0], size[1],
                           pix_fmt, gl.GL_UNSIGNED_BYTE, img)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    
    def _guess_internal_fmt(self, img: np.ndarray):
        ch = img.shape[-1]
        if   ch == 1: return gl.GL_RED
        elif ch == 3: return gl.GL_RGB
        elif ch == 4: return gl.GL_RGBA
        else:
            raise ValueError("Wrong shape: {}".format(img.shape))

    def _guess_pix_fmt(self, img: np.ndarray, is_bgr: bool):
        ch = img.shape[-1]
        if   ch == 1: return gl.GL_RED
        elif ch == 3: return gl.GL_BGR  if is_bgr else gl.GL_RGB
        elif ch == 4: return gl.GL_BGRA if is_bgr else gl.GL_RGBA
        else:
            raise ValueError("Wrong shape: {}".format(img.shape))

    def __del__(self):
        self._reset()
        # print("Destroy image")
