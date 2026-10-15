require 'imlib2'

function conky_dibujar_fondo()
    if conky_window == nil then
        return
    end

    local imagen = imlib_load_image(
        "/home/natedum/.config/conky/sprites/pom.png"
    )

    if imagen == nil then
        return
    end

    imlib_context_set_image(imagen)

local ancho = imlib_image_get_width()
local alto = imlib_image_get_height()

imlib_context_set_drawable(conky_window.drawable)
imlib_context_set_blend(0)
imlib_render_image_on_drawable_at_size(0, 0, 420, 600)

    imlib_free_image()
end