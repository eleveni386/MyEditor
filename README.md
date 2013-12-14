MyEditor
========

A markdown Editor

#功能

一个简单的markdown文本编辑器, 提供webkit来显示markdown转换的html页面

#依赖

1. pygtk
2. python-markdown
3. python-webkit
4. python-gtksourceview2

debian 可以使用`apt-get` 来安装

#设置

**themes**

*textview* 

编辑器 主题文件 

*webkit*

webkit 主题文件

*language-specs*

语法文件

由于默认的`gtksourceview2`没有`markdown`语法支持.
`MyEditor` 内置了`markdown`的支持

#截图

![](http://eleveni386.7axu.com/image/markdown.png)

#模块

###文件管理器

一个简单的文件管理器. 用于管理松散的markdown文件

默认会在家目录下建立一个.mybase的隐藏目录. 每次程序启动的时候 自动加载这个目录.

因此 可以将本程序当成markdown笔记本来使用

###编辑器

使用`gtksourceview2` 

拥有markdown语法高亮

###Webkit

没啥好说的. 用于显示markdown转换之后的html而已

恩,可以设置style, 默认使用github的风格.css文件在themes目录下

#鸣谢

网友 " 老猫 "
网友 [" 小邪兽 "](http://neteue.com/)

#主页

["eleveni386"](http://eleveni386.7axu.com)
