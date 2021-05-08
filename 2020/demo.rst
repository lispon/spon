###############################################################
Demo 测试
###############################################################

********************************************************************************
图片
********************************************************************************

.. warning::
    图片不能放在 **_static** 目录下. 在生成html时, 会自动将所有图片自动复制到 **index.html** 所在目录的 **_images** 文件夹中, 同时引用路径也会更改为相对路径.

    而且 **_static** 目录中的所有内容, 会原封不动的复制到对应的 **_static** 目录中, 如果把图片放在该文件夹中.

.. image:: images/200px-Rotating_earth_(large).gif
    :width: 200px
    :height: 200px
    :scale: 100
    :align: center
    :alt: alternate text
    :target: https://www.baidu.com

.. note::
    
    图片有六种自定义的行为:

    1. **alt:** 图片不存在时, 显示的文本.

    2. **height:** 设置图片的高度, 单位是像素.

    3. **width:** 设置图片的宽度, 单位是像素.

    4. **scale:** 设置图片的缩放比例. 单位1%. 百分号可省略不写.

    5. **align:** 图片的对齐方式, 水平对齐方式 left, center, right. 经测试, 垂直对齐方式 top, middle, bottom 暂不生效.

    6. **target:** url超链接, 或引用. 点击跳转.


********************************************************************************
代码
********************************************************************************

#. 代码一

this is a inline code: ``std::cout << "hello world!";``.

#. 代码二

this is a single code ::

    int main() {
      std::cout << "hello world!";
      return 1;
    }

#. 代码三

.. code:: c

    class a;
    int main() {
       std::cout << "hello world!";
       return 1;
    }

.. code-block:: c++
    :linenos:
    :lineno-start: 10
    :emphasize-lines: 1, 3-5
    :caption: caption
    :dedent: 4

        class a;
        int main() {
          std::cout << "hello world!\n";
          for(int i = 0; i < 10; i++) {
            std::cout << i << std::endl;
          }
          return 1;
        }

.. note::

    #. linenos 显示代码左侧的行序号.
    #. lineno-start 行序号开始的数字, 自动启用linenos.
    #. emphasize-lines 高亮代码的行序号, 支持使用减号表示行范围, 逗号表示间隔.
    #. caption 行标题.
    #. name 
    #. dedent 从代码块中去除缩进字符, 即将代码块整体向左移动(即使左侧字符不为空).
    #. force


********************************************************************************
脚注 (Footnotes)
********************************************************************************

Lorem ipsum [#]_ dolor sit amet ... [#]_.

.. rubric:: Footnotes

.. [#] Text of the first footnote.
.. [#] Text of the second footnote.
.. [#] 前面的序号, 在整个文章中, 后顺序排列下去. 即使在其他地方的脚注也会排序.


********************************************************************************
引文 (Citations)
********************************************************************************

Lorem ipsum [Ref]_ dolor sit amet.

.. [Ref] Book or article reference, URL or whatever.

Here is a citation reference: [CIT2002]_.

.. [CIT2002] This is the citation.  It's just like a footnote,
   except the label is textual.


********************************************************************************
替换 (Substitutions)
********************************************************************************

.. |name| replace:: spon

my name is |name|.


.. |picture| image:: images/200px-Rotating_earth_(large).gif
             :scale: 10

my picture is |picture|.


********************************************************************************
注释 (comment)
********************************************************************************


.. this is a comment.


********************************************************************************
超链接 (Hyperlink targets)
********************************************************************************


#. 内部超链接:

    允许链接到另一个地方或本文档的一个位置.

    Clicking on this internal hyperlink will take us to the target_
    below.
    
    .. _target: https://www.baidu.com
    
    The hyperlink target above points to this paragraph.

    .. _target1:
    .. _target2: https://www.google.com
    
    The targets "target1_" and "target2_" are synonyms; they both
    point to this paragraph. 两个相邻的超链接, 指向的url相同, 只需定义最后一个超链接.

#. 外部超链接:

    See the Python_ home page for info.
    
    `Write to me`_ with your questions.
    
    .. _Python: http://www.python.org
    .. _Write to me: jdoe@example.com

    超链接内容, 可以使用空格换行, 如下.

    .. _one-liner: https://docutils.sourceforge.net/rst.html
    
    .. _starts-on-this-line: https://docutils.sourceforge.net/rst.html
    
    .. _entirely-below: https://docutils.sourceforge.net/rst.html

    one-liner_, starts-on-this-line_, entirely-below_.

`Demo 测试`_

请参见 代码_
