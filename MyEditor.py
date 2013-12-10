#!/usr/bin/python
#coding=utf8
#Author : eleven.i386
#Email  : eleven.i386@gmail.com
#Site   : eleveni386.7axu.com
#Date   : 13-09-24
#DES	:

import pygtk
pygtk.require('2.0')
import gtk
import os
import getpass
import gobject
import shutil
import subprocess
import markdown
import webkit
import gtksourceview2
import gtk.gdk as gdk

CURRENTPATH = os.path.abspath(os.path.split(__file__)[0])

#----------------------------------
STATE_POOL = {}
WWBKITTHEME = '%s/themes/webkit/github.css'%CURRENTPATH
TEXTVIEW_PATH = ['%s/themes/textview/'%CURRENTPATH]
TEXTVIEW_STYLE = 'cobalt'
LANGUAGE_PATH = ['%s/language-specs/'%CURRENTPATH]
ICON = '%s/icon/M.ico'%CURRENTPATH
#---------------------------------

if os.getuid() != 0:

    BASEDIRTORY = '/home/%s/.mybase'%(getpass.getuser())

    if not os.path.exists(BASEDIRTORY):
        os.mkdir(BASEDIRTORY)

else:

    print '无法在root下使用'
    sys.exit(1)

def destory_state():

    if '未保存' in ''.join(STATE_POOL.values()):

        msg = '您有未保存的文件!\n\n%s\n\n您确定不保存,而退出?'%(
                ''.join([ i[1].split()[0].split('/')[-1]+'\n'
                    for i in STATE_POOL.items()
                    if i[1].split()[-1] == '未保存' ])
                )

        w = gtk.MessageDialog(None,
                gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION,
                gtk.BUTTONS_YES_NO,
                msg)

        r = w.run()

        if r == gtk.RESPONSE_YES:
            w.destroy()
            return False

        if r == gtk.RESPONSE_NO:
            w.destroy()
            return True
    else:
        return False

class Webkit():

    def __init__(self):

        self.webview =  webkit.WebView()
        self.sw = gtk.ScrolledWindow()
        self.sw.add(self.webview)
        self.sw.hide()

    def view(self, stylescheme, markdown_file):
        fp = open('/home/eleven/view.html','w')
        html = """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="utf-8">
            <style type="text/css">
            %s
            </style>
        </head>
        <body>
            %s
        </body>
        </html>
            """%(stylescheme,markdown.markdown(markdown_file))

        fp.write(html)

        self.webview.load_html_string(html,'')
        self.webview.show_all()

    def webkit_obj(self):

        return self.sw

class Notebook():

    def __init__(self):
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(True)
        self.notebook.set_scrollable(True)
        self.notebook_Label_Manager = {}

    def add_Page(self, widget, Label=''):

        if self.notebook_Label_Manager.has_key(Label):
            self.set_current_Page(Label)
        else:
            notebook_label = self.close_label(widget, Label)
            self.notebook.append_page(widget, notebook_label)

            self.notebook_Label_Manager[Label] = (
                    self.notebook.page_num(widget),widget
                    )
            self.notebook.show_all()

    def update_Page(self, Oldlabel='', Newlabel='', obj=''):

        if obj == 'dir':

            for key,value in self.notebook_Label_Manager.items():

                del self.notebook_Label_Manager[key]

                self.notebook_Label_Manager[
                    key.replace(Oldlabel,Newlabel)
                        ] = value

        elif obj == 'file':

            num,widget = self.notebook_Label_Manager[Oldlabel]

            Newlabel = Oldlabel.replace(Oldlabel,Newlabel)

            self.notebook_Label_Manager[Newlabel] = (num,widget)

            self.notebook.set_tab_label(widget,self.close_label(widget,Newlabel))
            self.set_current_Page(Newlabel)

        self.notebook.show_all()

    def set_current_Page(self, Label):

        page_num = self.notebook_Label_Manager[Label][0]
        self.notebook.set_current_page(page_num)

    def close_label(self, page, text=''):

        box = gtk.HBox()
        Label = gtk.Label(text.split('/')[-1])
        file_type_image = gtk.Image()
        file_type_image.set_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_SMALL_TOOLBAR)
        close_image = gtk.Image()
        close_image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button = gtk.Button()
        close_button.set_image(close_image)
        close_button.set_relief(gtk.RELIEF_NONE)
        close_button.connect('clicked', self.destroy_tab, page, text)
        box.pack_start(file_type_image, False,False,0)
        box.add(Label)
        box.pack_end(close_button, False, False,0)
        box.show_all()

        return box

    def destroy_tab(self, widget, data, label_text):

        if destory_state():
            return False
        else:

            page_num = self.notebook.page_num(data)

            self.notebook.remove_page(page_num)

            del self.notebook_Label_Manager[
                [
                    i for i in self.notebook_Label_Manager.keys()
                    if self.notebook_Label_Manager[i][0] == page_num
                        ][0]
                ]

            del STATE_POOL[label_text]

            for i in self.notebook_Label_Manager.keys():

                if page_num < self.notebook_Label_Manager[i][0] \
                and self.notebook_Label_Manager[i][0] != 0:

                    self.notebook_Label_Manager[i] = (
                            self.notebook_Label_Manager[i][0] - 1,
                            self.notebook_Label_Manager[i][1])

            return True

    def nbook(self):
        return self.notebook

class TextView():
    def __init__(self):

        self.lm = gtksourceview2.LanguageManager()
        self.lm.set_search_path(LANGUAGE_PATH)
        self.Sm = gtksourceview2.StyleSchemeManager()
        self.Sm.set_search_path(TEXTVIEW_PATH)
        self.sourceview = gtksourceview2.View()
        self.sourceview.set_show_right_margin(True)
        self.sourceview.set_show_line_numbers(True)
        self.sourceview.set_highlight_current_line(True)
        self.sourceview.set_auto_indent(True)
        self.sourceview.set_insert_spaces_instead_of_tabs(True)
        self.sourceview.set_tab_width(4)
        self.buff = gtksourceview2.Buffer()
        self.buff.set_max_undo_levels(5)
        self.buff.connect('changed', self.buff_change)
        self.change = False
        self.sourceview.connect("key-press-event",self.key_press)

        self.filepath = ''
        self.statusbar = gtk.Statusbar()
        self.sourceview.set_editable(False)

    def buff_change(self, widget):
        if self.change:
            self.status_push(self.filepath,'%s 未保存'%self.filepath.split('/')[-1])
        self.change = True

    def key_press(self, widget, event):

        if event.state & gdk.CONTROL_MASK and str(unichr(event.keyval)) == 's':
            self.save_file(widget,self.filepath)
            self.status_push(self.filepath,'%s 已保存'%self.filepath.split('/')[-1])
            self.change = False

        elif event.state & gdk.CONTROL_MASK and str(unichr(event.keyval)) == 'z':
            if self.buff.can_undo():
                self.buff.undo()
            self.status_push(self.filepath,'%s 未保存'%self.filepath.split('/')[-1])
            self.change = True

    def status_push(self, id, context):

        if not STATE_POOL.has_key(id) or STATE_POOL[id] != context:
            STATE_POOL[id] = context
        self.statusbar.push(self.statusbar.get_context_id(id),STATE_POOL[id])

    def editable(self,Bool):
        self.sourceview.set_editable(Bool)

    def clear_buf(self):
        begin, end = self.buff.get_bounds()
        self.buff.delete(begin,end)

    def load_file(self, filename):

        self.status_push(filename,'Current: %s'%filename.split('/')[-1])

        self.buff.set_data('languages-manager', self.lm)

        if os.path.isabs(filename):
            self.filepath = filename
        else:
            self.filepath = os.path.abspath(filename)

        manager = self.buff.get_data('languages-manager')
        stylescheme = self.Sm.get_scheme(TEXTVIEW_STYLE)
        self.buff.set_style_scheme(stylescheme)

        language = manager.guess_language(filename)

        if language:
            self.buff.set_highlight_syntax(True)
            self.buff.set_language(language)
        else:
            self.buff.set_highlight_syntax(False)

        self.buff.begin_not_undoable_action()
        txt = open(self.filepath).read()
        self.buff.set_text(txt)
        self.buff.set_data('filename', self.filepath)
        self.buff.end_not_undoable_action()
        self.buff.place_cursor(self.buff.get_start_iter())
        self.sourceview.set_buffer(self.buff)

        return True

    def save_file(self, widget, filename):

        buf = widget.get_buffer()
        start, end = buf.get_bounds()
        textbuf = buf.get_text(start,end)

        if os.path.isabs(filename):
            path = filename
        else:
            path = os.path.abspath(filename)

        fp = open(path,'w')
        fp.write(textbuf)
        fp.close()

        return True

    def textview(self):

        sw = gtk.ScrolledWindow()
        vbox = gtk.VBox()
        sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        sw.add(self.sourceview)
        vbox.pack_start(sw)
        vbox.pack_end(self.statusbar,expand=False)

        return vbox


class FileBrowser():

    def __init__(self, HomeDir):

        self.default_dir = HomeDir
        self.expand_Flag = False
        self.treestore = gtk.TreeStore(str, str, str)
        self.notebook = Notebook()
        self.webkit = Webkit()
        self.load_dir(self.default_dir)

        self.treeview = gtk.TreeView(self.treestore)
        self.model = self.treeview.get_model()
        self.treeview.set_rules_hint(True)
        self.treeview.set_enable_tree_lines(True)
        self.treeview.set_size_request(200,-1)
        self.treeview.connect("button-press-event", self.button_press)

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()

        column = gtk.TreeViewColumn('More... Click Me')
        column.pack_start(cellpb,False)
        column.pack_start(cell,True)
        column.set_attributes(cellpb, stock_id = 2)
        column.set_attributes(cell, text = 0)
        column.set_clickable(True)
        column.connect("clicked", self.chooserFile)

        self.treeview.append_column(column)

    def file_filter(self, filepath):

        cmd = 'file --mime-type "%s"'%filepath

        r = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                shell=True).stdout.read()

        if 'text' in r or 'x-empty' in r :return True

        return False

    def load_dir(self, dirpath):

        dirname = os.path.abspath(dirpath)

        fiter = None

        if os.path.isdir(dirname):

            fiter = self.treestore.append(
                    None,[dirpath.split('/')[-1],dirname,gtk.STOCK_DIRECTORY]
                    )

        dir_iter_dir = {dirname:fiter}

        for dirpath, dirnames, filenames in os.walk(dirname):

            for directory in dirnames:

                abspath = os.path.join(dirpath,directory)

                iterator = self.treestore.append(
                        dir_iter_dir[dirpath],
                        [directory,abspath, gtk.STOCK_DIRECTORY]
                        )

                dir_iter_dir[abspath] = iterator

            for filename in filenames:

                if self.file_filter(os.path.join( dirpath ,filename)):

                    self.treestore.append(
                            dir_iter_dir[dirpath],
                            [filename, os.path.join(dirpath, filename),
                            gtk.STOCK_FILE]
                            )
                    #print filename,os.path.join(dirpath,filename)


    def chooserFile(self,event):

        chooser = gtk.FileChooserDialog(
                '其他目录',
                None,
                #gtk.FILE_CHOOSER_ACTION_OPEN,
                gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                (
                    gtk.STOCK_CANCEL,
                    gtk.RESPONSE_CANCEL,
                    gtk.STOCK_OPEN,
                    gtk.RESPONSE_OK
                )
        )

        filter = gtk.FileFilter()
        filter.set_name('All Files')
        filter.add_pattern('*')
        chooser.add_filter(filter)
        res = chooser.run()

        if res == gtk.RESPONSE_OK:
            self.load_dir(chooser.get_filename())

        chooser.destroy()

    def msg_dialog(self,title=None, parent=None, flags=0, buttons=None, msg=None):
        dialog = gtk.Dialog(title, parent, flags, buttons)
        dialog.vbox.pack_start(gtk.Label(msg))
        dialog.show_all()

        return dialog

    def warn_dialog(self, msg):
        warning = self.msg_dialog('错误',None,gtk.DIALOG_DESTROY_WITH_PARENT,
                                (gtk.STOCK_CLOSE,gtk.BUTTONS_CLOSE),msg)
        warning.run()
        warning.destroy()

    def responsetodialog(self,entry, dialog, response):
        dialog.response(response)

    def text_dialog(self, title):

        text = ''

        dialog = self.msg_dialog(title,None,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL,gtk.BUTTONS_CANCEL,
                            gtk.STOCK_OK,gtk.BUTTONS_OK), '名称什么的真的随便啦!')

        entry = gtk.Entry()

        entry.connect("activate", self.responsetodialog, dialog,gtk.RESPONSE_OK)

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(),False, 5,5)
        hbox.pack_end(entry)
        dialog.vbox.pack_end(hbox)
        dialog.show_all()
        r = dialog.run()

        if r == gtk.RESPONSE_OK:
            text = entry.get_text()

        dialog.destroy()

        return text

    def filebrowser(self):
        sw = gtk.ScrolledWindow()
        sw.add(self.treeview)

        return (sw,self.notebook.nbook(),self.webkit.webkit_obj())

    def newfile(self,event,path,model):

        text = self.text_dialog('新建文档')
        if not text : return True

        filepath = model.get_value(model.get_iter(path),1)

        os.mknod(os.path.join(filepath,text))

        self.webkit.view(open(WWBKITTHEME,'r').read(),
                open(os.path.join(filepath,text),'r').read())

        self.treestore.append(model.get_iter(path),[text,os.path.join(
                            filepath,text),gtk.STOCK_FILE])
        return True

    def newdir(self,event, path,model):

        text = self.text_dialog('新建目录')
        if not text : return True
        filepath = model.get_value(model.get_iter(path),1)
        os.mkdir(os.path.join(filepath,text))

        self.treestore.append(model.get_iter(path),[text,os.path.join(
                       filepath,text),gtk.STOCK_DIRECTORY])
        return True

    def re_name(self,event, path, model):

        filename = self.text_dialog('重命名')
        if not filename : return True

        oldfilename = model.get_value(model.get_iter(path),1).split('/')[-1]
        parent_path = model.get_value(model.iter_parent(model.get_iter(path)),1)

        filepath = os.path.join(parent_path,oldfilename)

        #print 'filepath', filepath

        newfilepath = os.path.join(parent_path,filename)

        #print 'rename filepath %s newfilepath %s'%(filepath,newfilepath)

        os.rename(filepath,newfilepath)

        self.treestore.set(model.get_iter(path),0,filename)
        self.treestore.set(model.get_iter(path),1,newfilepath)

        if not os.path.isdir(newfilepath):

            self.treestore.set(model.get_iter(path),2,gtk.STOCK_FILE)
            self.notebook.update_Page(filepath,newfilepath,'file')
            self.webkit.view(open(WWBKITTHEME,'r').read(),
                    open(newfilepath,'r').read())
        else:
            self.notebook.update_Page(filepath,newfilepath,'dir')
            self.treestore.set(model.get_iter(path),2,gtk.STOCK_DIRECTORY)

        return True

    def delfile(self,event, path, model):

        filepath = model.get_value(model.get_iter(path),1)
        rootpath = model.get_value(model.get_iter_root(),1)

        if filepath == rootpath:
            self.warn_dialog('这个目录不可以删除哦')
            return True

        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)
        self.treestore.remove(model.get_iter(path))

        return True

    def childMenu(self, event, path, model ):
        menu = gtk.Menu()
        rename = gtk.MenuItem("重命名")
        menu.append(rename)
        rename.connect("activate", self.re_name, path, model)

        del_file = gtk.MenuItem("删除")
        menu.append(del_file)
        del_file.connect("activate", self.delfile, path, model)

        menu.popup(None, None, None, event.button, event.time,None)
        menu.show_all()

        return True

    def ALLMenu(self, event, path, model ):
        menu = gtk.Menu()
        new_file = gtk.MenuItem("新建笔记")
        menu.append(new_file)
        new_file.connect("activate", self.newfile, path, model)

        new_dir = gtk.MenuItem("新建目录")
        menu.append(new_dir)
        new_dir.connect("activate", self.newdir, path, model)

        sep = gtk.SeparatorMenuItem()
        menu.append(sep)

        rename = gtk.MenuItem("重命名")
        menu.append(rename)
        rename.connect("activate", self.re_name, path, model)

        del_file = gtk.MenuItem("删除")
        menu.append(del_file)
        del_file.connect("activate", self.delfile, path, model)

        menu.popup(None, None, None, event.button, event.time,None)
        menu.show_all()

        return True

    def node_select(self, path, model):

        self.treeview.grab_focus()

        if not self.expand_Flag:
            self.treeview.expand_row(path,False)
            self.expand_Flag = True
        else:
            self.treeview.collapse_row(path)
            self.expand_Flag = False
        return True

    def open_node(self, path, model):

        self.txtview = TextView()

        filename = model.get_value(model.get_iter(path),0)
        parent_path = model.get_value(model.iter_parent(model.get_iter(path)),1)
        filepath = os.path.join(parent_path,filename)

        #print 'filepath %s'%filepath

        if self.file_filter(filepath) and not model.iter_has_child(model.get_iter(path)):

            self.txtview.editable(True)
            self.txtview.load_file(filepath)
            textview = self.txtview.textview()

            #print 'current Page: %s'%filepath

            self.notebook.add_Page(textview, filepath)

            self.notebook.set_current_Page(filepath)
            self.webkit.view(open(WWBKITTHEME,'r').read(),open(filepath,'r').read())

        else:
            self.txtview.editable(False)

        return True

    def button_press(self,widget, event):
        x, y = map(int, [event.x, event.y])
        try:
            path, col, cellx, celly = widget.get_path_at_pos(x, y)

        except TypeError:
            return True

        model = widget.get_model()
        if event.type == gdk._2BUTTON_PRESS:
            self.open_node(path, model)
        if event.button == 1:
            self.node_select(path, model)
        if event.button == 3:
            time = event.time
            widget.grab_focus()
            selection = widget.get_selection()
            if not selection.path_is_selected(path):
                widget.set_cursor(path, col, 0)
            col.focus_cell(col.get_cell_renderers()[0])

            if os.path.isdir(model.get_value(model.get_iter(path),1)):
            #if model.iter_has_child(model.get_iter(path)):
                self.ALLMenu(event, path, model)
            else:
                self.childMenu(event, path, model)

            return True

class MainWindow():

    def __init__(self,title="MyEditor",width=800,height=600):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title(title)
        self.window.set_icon_from_file(ICON)
        self.window.set_size_request(width, height)
        self.window.maximize()
        self.window.connect("delete_event", self.delete_event)

        self.CFB = FileBrowser(BASEDIRTORY)
        self.Fb, self.notebook, self.webkit = self.CFB.filebrowser()

        self.Fb_hide = True
        self.Wk_show = True

        self.mb = gtk.MenuBar()

        filemenu = gtk.Menu()
        setmenu = gtk.Menu()
        helpmenu = gtk.Menu()
        filem = gtk.MenuItem('文件(_F)')
        setm = gtk.MenuItem('编辑(_E)')
        helpm = gtk.MenuItem('帮助(_H)')
        filem.set_submenu(filemenu)
        setm.set_submenu(setmenu)
        helpm.set_submenu(helpmenu)

        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about.set_label('关于(_A)')
        about.connect('activate',self.About)
        helpmenu.append(about)

        md = gtk.CheckMenuItem('Webkit View')
        md.set_active(False)
        md.connect('activate',self.WebkitHide)
        setmenu.append(md)

        fb = gtk.CheckMenuItem('Hide FileManager')
        fb.set_active(False)
        fb.connect('activate',self.FMHide)
        setmenu.append(fb)

        exit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        exit.connect('activate', self.delete_event)
        exit.set_label('退出(_Q)')
        filemenu.append(exit)

        self.mb.append(filem)
        self.mb.append(setm)
        self.mb.append(helpm)

        self.toolbar = gtk.Toolbar()
        self.toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.toolbar.set_border_width(0)

    def About(self, widget, event=None):

        about = gtk.AboutDialog()
        about.set_program_name("MyEditor")
        about.set_version("Beta 0.1")
        about.set_copyright("(c) eleven i386")
        about.set_comments("这是一个markdown编辑器")
        about.set_website("http://eleveni386.7axu.com")
        about.set_logo(gtk.gdk.pixbuf_new_from_file(ICON))
        about.run()
        about.destroy()

    def FMHide(self,widget,event=None):
        if self.Fb_hide:
            self.Fb.hide()
            self.Fb_hide = False
        else:
            self.Fb.show_all()
            self.Fb_hide = True

    def WebkitHide(self,widget,event=None):
        if self.Wk_show:
            self.webkit.show_all()
            self.Wk_show = False
        else:
            self.webkit.hide()
            self.Wk_show = True

    def main(self):


        HSep1 = gtk.HSeparator()

        head = gtk.VBox(False,2)
        head.pack_start(self.mb, False, False, 0)
        head.add(HSep1)
        head.add(self.toolbar)

        vbox = gtk.VBox(False,2)
        vbox.pack_start(head, False, False, 0)

        HBox = gtk.HBox()
        HBox.pack_start(self.Fb, False, False, 1)
        HBox.add(self.notebook)

        HBox.pack_end(self.webkit,True,True,1)
        vbox.pack_end(HBox, True, True, 0)

        self.window.add(vbox)
        self.window.show_all()
        self.webkit.hide()

        gtk.main()

    def delete_event(self, widget, event=None):

        if not destory_state():
            gtk.main_quit()
            return False
        else:
            return True

a = MainWindow()
a.main()
