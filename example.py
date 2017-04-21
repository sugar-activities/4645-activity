#!/usr/bin/python
import gtk, gobject, random, pango

DELAY = 8
WIDTH = 600
HEIGHT = 600

class MyApp():
    
    def __init__(self):
        window = gtk.Window()
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        
        #se usaran para el marcador
        self.label = gtk.Label()
        self.label.modify_font(pango.FontDescription("Purisa 14"))
        frame = gtk.Frame("Marcador")
       
        #asignacion de variables a widgest de gtk
        self.vadjustment = gtk.Adjustment()
        self.hadjustment = gtk.Adjustment()
        
        #asignacion de valores por defecto del adjustment
        self.vadjustment.set_upper(100)
        self.vadjustment.set_value(0)
        self.hadjustment.set_upper(100)
        self.hadjustment.set_value(0)
        
        #asignacion de propiedades de widgets
        self.vslide = gtk.VScale(self.vadjustment)
        self.hslide = gtk.HScale(self.hadjustment)
        #propiedad para que no se muestre valor del slide
        self.vslide.set_draw_value(False)
        self.hslide.set_draw_value(False)
        
        #variables globales que se utilizan en los slides
        self.increment_x = self.increment_y = 1
        self.indicator_x = self.indicator_y = -1
        self.goles = 0
        self.atajadas = 0
        
        #asignacion de variables de widgets
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.set_size_request(WIDTH, HEIGHT)
            
        #asignando cancha y arquero
        self.cancha = gtk.gdk.pixbuf_new_from_file('images/arco.jpg')
        self.portero = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_downcenter.png')
        
        window.connect("destroy", lambda w: gtk.main_quit())
        
        #callbacks al invocar el area de dibujo
        self.drawing_area.connect('configure_event', self.__configure_cb)
        self.drawing_area.connect('expose-event', self.__expose_cb)
        
        #evento que invoca funcion al presionar cualquier tecla
        window.connect('key-press-event', self.__key_press_event_cb)
        
        #anhadiendo widgets dentro del contenedor principal
        window.add(hbox)
        hbox.add(vbox)
        frame.add(self.label)
        vbox.add(frame)
        vbox.add(self.drawing_area)
        vbox.add(self.hslide)
    	hbox.add(self.vslide)
        
        #mostrando los widgets
        window.show_all()
        
        #invocacion de la funcion que realiza loop del slider horizontal
        gobject.timeout_add(DELAY, self.__hslider_move_cb)
        
    def dibujar_portero_y_cancha(self):
        self.pixmap.draw_pixbuf(None, self.cancha, 0, 0, 0, 0, -1, -1,
                                gtk.gdk.RGB_DITHER_NONE, 0, 0)
        self.pixmap.draw_pixbuf(None, self.portero, 0, 0, 0, 200, -1, -1,
                                gtk.gdk.RGB_DITHER_NONE, 0, 0)
                                
    #funcion que se activa al presionar cualquier tecla y pregunta sobre el estado de los indicadores
    def __key_press_event_cb(self, window, event):
        if self.indicator_x == -1 and self.indicator_y == -1:
        
            self.capturar_valor_hslider()
            gobject.timeout_add(DELAY, self.__vslider_move_cb)
            
        elif self.indicator_y == -1:
            self.capturar_valor_vslider()
            
            #lanzar portero
            self.goal_keeper()
            
            #invoca a la funcion que dibuja la pelota de acuerdo a los valores de los sliders
            self.draw_ball(self.cv_x,self.cv_y)
            
            #metodo que refresca el drawing_area para actualizar posicion del portero y pelota
            self.drawing_area.queue_draw()
        else:
        
            #llamado a la funcion que restaura el juego
            self.restart_game()
            gobject.timeout_add(DELAY, self.__hslider_move_cb)
            
    #funcion que restaura el juego        
    def restart_game(self):
    
        self.dibujar_portero_y_cancha()
        
        #metodo que refresca el drawing_area
        self.drawing_area.queue_draw()
        
        self.increment_x = self.increment_y = 1
        self.indicator_x = self.indicator_y = -1
        self.hadjustment.value = self.vadjustment.value = 0
        
        #llamado a la funcion que actualiza el marcador
        self.marcador()
    
    #funcion que actualiza el marcador
    def marcador(self):
        if self.goles == 1:
            self.label.set_text(str(self.goles)+' '+'Gol hasta ahora!')
        elif self.goles > 1:
            self.label.set_text(str(self.goles)+' '+'Goles hasta ahora!')
    
    #funcion que dibuja y lanza al arquero en alguna posicion      
    def goal_keeper(self):

        self.pixmap.draw_pixbuf(None, self.cancha, 0, 0, 0, 0, -1, -1,
                                gtk.gdk.RGB_DITHER_NONE, 0, 0)
                                
        pixbufkeeper_DC = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_downcenter.png')
        pixbufkeeper_DL = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_downleft.png')
        pixbufkeeper_DR = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_downright.png')
        pixbufkeeper_UC = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_upcenter.png')
        pixbufkeeper_UL = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_upleft.png')
        pixbufkeeper_UR = gtk.gdk.pixbuf_new_from_file('images/goalkeeper_upright.png')
        
        pos_portero = [pixbufkeeper_DC, pixbufkeeper_DL, pixbufkeeper_DR,
                       pixbufkeeper_UC, pixbufkeeper_UL, pixbufkeeper_UR]
        self.r = random.randint(0,5)
        #invocacion de forma random al pixbuf del arquero para que se lance en una posicion
        self.portero_ran = pos_portero[self.r]
        self.pixmap.draw_pixbuf(None, self.portero_ran, 0, 0, 0, 200, -1, -1,
                                gtk.gdk.RGB_DITHER_NONE, 0, 0)

    #funcion que hace el loop de los valores del slider horizontal   
    def __hslider_move_cb(self):
        if self.indicator_x < 0:
            self.hadjustment.value += self.increment_x
        
            if self.hadjustment.value >= 100:
    	        self.increment_x *= -1
            elif self.hadjustment.value <= 0:
    	        self.increment_x *= -1
            return True
        else:
            return False
    
    #funcion que hace el loop de los valores del slider vertical
    def __vslider_move_cb(self):
        if self.indicator_y < 0:
            self.vadjustment.value += self.increment_y
        
            if self.vadjustment.value >= 100:
    	        self.increment_y *= -1
            elif self.vadjustment.value <= 0:
    	        self.increment_y *= -1
            return True
        else:
            return False

    #funcion que captura el valor del slider horizontal despues de pulsar una tecla    
    def capturar_valor_hslider(self):
    
        #variable en donde se captura el valor al presionar un tecla
        self.hslide_value = self.hslide.get_value()

        #convierte el valor de changed_value a int
        self.cv_x = (((int(self.hslide_value)) * WIDTH) / 100)
        
        #detiene el slider
        self.indicator_x = 0
    
    #funcion que captura el valor del slider vertical despues de pulsar una tecla    
    def capturar_valor_vslider(self):
    
        #variable en donde se captura el valor al presionar un tecla
        self.vslide_value = self.vslide.get_value()
        
        #convierte el valor de changed_value a int
        self.cv_y = (((int(self.vslide_value)) * HEIGHT) / 100)
        
        #detiene el slider
        self.indicator_y = 0
        
    #funcion que dibuja la pelota
    def draw_ball(self, x, y):
    
        #variables de las dimensiones de la pelota
        self.c_x = x
        self.c_y = y
        self.c_a = 110
        self.c_h = 99
        
        #calculo de posicion de valor exacto de la pelota con relacion a los slides
        Xm = self.c_x - (self.c_a / 2)
        Ym = self.c_y - (self.c_h / 2)
        
        #dibujando la pelota con un pixbuf de acuerdo a valores de los slides
        self.pelota = gtk.gdk.pixbuf_new_from_file('images/ball.png')
        self.pixmap.draw_pixbuf(self.context, self.pelota, 0, 0, Xm, Ym, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        
        #calcular el gol con las coordenadas de la pelota
        self.calculo_gol(Xm, Ym)
    
    def calculo_gol(self, c_x, c_y):
        #Coordenadas del rectangulo interior del arco
        i_x = 58
        i_y = 144
        i_a = 484
        i_l = 324
        
        if c_x > i_x and c_y > i_y and c_x < i_x+i_a and c_y < i_y+i_l:
            
            if self.r == 0:
                if c_x > 210 and c_x < 388 :
                    if c_y > 222 and c_y < 490:
                        self.label.set_text('EL ARQUERO ATAJA!!!')
                    else:
                        self.label.set_text('GOOOL!!!')
                        self.goles = self.goles + 1
                else:
                    self.label.set_text('GOOOL!!!')
                    self.goles = self.goles + 1                    
            elif self.r == 1:
                if c_x > 156 and c_x < 451:
                    if c_y > 345 and c_y < 500:
                        self.label.set_text('EL ARQUERO ATAJA!!!')
                    else:
                        self.label.set_text('GOOOL!!!')
                        self.goles = self.goles + 1
                else:
                    self.label.set_text('GOOOL!!!')
                    self.goles = self.goles + 1
            elif self.r == 2:
                if c_x > 147 and c_x < 448:
                    if c_y > 347 and c_y < 500:
                        self.label.set_text('EL ARQUERO ATAJA!!!')
                    else:
                        self.label.set_text('GOOOL!!!')
                        self.goles = self.goles + 1
                else:
                    self.label.set_text('GOOOL!!!')
                    self.goles = self.goles + 1
            elif self.r == 3:
                if c_x > 169 and c_x < 428:
                    if c_y > 246 and c_y < 451:
                        self.label.set_text('EL ARQUERO ATAJA!!!')
                    else:
                        self.label.set_text('GOOOL!!!')
                        self.goles = self.goles + 1
                else:
                    self.label.set_text('GOOOL!!!')
                    self.goles = self.goles + 1
            elif self.r == 4:
                if c_x > 179 and c_x < 416:
                    if c_y > 239 and c_y < 475:
                        self.label.set_text('EL ARQUERO ATAJA!!!')
                    else:
                        self.label.set_text('GOOOL!!!')
                        self.goles = self.goles + 1
                else:
                    self.label.set_text('GOOOL!!!')
                    self.goles = self.goles + 1
            elif self.r == 5:
                if c_x > 182 and c_x < 422:
                    if c_y > 240 and c_y < 469:
                        self.label.set_text('EL ARQUERO ATAJA!!!')
                    else:
                        self.label.set_text('GOOOL!!!')
                        self.goles = self.goles + 1
                else:
                    self.label.set_text('GOOOL!!!')
                    self.goles = self.goles + 1
        else:
            print self.label.set_text('UFF... EL BALON VA AFUERA')
            
    def __configure_cb(self, drawing_area, data=None):
        x, y, width, height = drawing_area.get_allocation()

        canvas = drawing_area.window
        self.pixmap = gtk.gdk.Pixmap(canvas, width, height)
        self.dibujar_portero_y_cancha()
        
        return True

    def __expose_cb(self, drawing_area, data=None):
        x, y, width, height = data.area
        style = drawing_area.get_style()
        self.context = style.fg_gc[gtk.STATE_NORMAL]

        self.canvas = drawing_area.window
        self.canvas.draw_drawable(self.context, self.pixmap, x, y, x, y, width, height)

        return False

if __name__ == "__main__":
    my_app = MyApp()
    gtk.main()
