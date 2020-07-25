import sys, pathlib, os, shlex, logging

from gi.repository import Gtk, Gdk, GdkPixbuf

class Images:
    def __init__(self):
        self.images = [str(x) for x in pathlib.Path(".").glob("*") if x.is_file()]
        self.images.sort(key=os.path.getmtime)
        self.current_index = 0

    def next_image_filename(self):
        if self.current_index < len(self.images):
            self.current_index += 1
            return self.images[self.current_index - 1]
        else:
            return None

ims = Images()
                           
class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="pyimgsort")
        self.set_border_width(10)
        self.filename = None

        # box
        overlay = Gtk.Overlay()
        self.add(overlay)

        fixed = Gtk.Fixed()

        self.top_button = Gtk.Button("Click to begin")
        self.top_button.connect("clicked", self.picture_next)
        fixed.put(self.top_button, 5, 5)

        for i, d in enumerate(sys.argv[1:]):
            label = f"{d}"
            button = Gtk.Button(label)
            button.connect("clicked", self.picture_move)
            fixed.put(button, 5, 5 + (i+1) * 45)

        # image
        self.image = Gtk.Image()
        col = Gdk.Color(0,0,0)
        self.image.modify_bg(Gtk.StateType.NORMAL, col)
        overlay.add(self.image)
        overlay.add_overlay(fixed)

    def picture_next(self, widget):
        self.filename = ims.next_image_filename()
        if self.filename:
            self.orig_pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(self.filename))
            self.picture_rescale(None)

    def picture_move(self, widget):
        if self.filename:
            directory = widget.get_property("label")
            print(self.filename, directory)
            os.system(f"mkdir -p {shlex.quote(directory)}")
            os.system(f"mv {shlex.quote(str(self.filename))} {shlex.quote(directory)}")
        self.picture_next(None)

    def picture_rescale(self, widget):
        pheight = self.orig_pixbuf.get_height()
        pwidth = self.orig_pixbuf.get_width()

        print(pheight, pwidth)
        
        wwidth, wheight = self.get_size()

        print(wwidth, wheight)

        hrat = pheight / wheight
        wrat = pwidth / wwidth

        print(hrat, wrat)

        scale_factor = 1
        if hrat > 1 or wrat > 1:
            if hrat > wrat:
                scale_factor = hrat
            else:
                scale_factor = wrat
            print(scale_factor)
        else:
            if hrat < wrat:
                scale_factor = wrat
            else:
                scale_factor = hrat
            
        display_pixbuf = self.orig_pixbuf.scale_simple(pwidth // scale_factor, pheight // scale_factor, GdkPixbuf.InterpType.BILINEAR)
        
        self.image.set_from_pixbuf(display_pixbuf)
        top_btn_text = f"{self.filename} ({pwidth}x{pheight}) (image {ims.current_index}/{len(ims.images)}) scaled {int(scale_factor*10)/10} - click to skip"
        self.top_button.set_label(top_btn_text)
        
window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
