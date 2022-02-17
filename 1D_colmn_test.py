from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource,FuncTickFormatter, CustomJS, Slider, Panel, Range1d, Tabs, Button
from bokeh.plotting import Figure, output_file, show
import numpy as np
import math
from bokeh.embed import components
import os
import sys

# setting working sirectory to current folder
os.chdir(os.path.dirname(sys.argv[0]))


# Initial parameters
length = [x*0.0001 for x in range(-40, 2000)]
c0 = 1
time  = 21636
velocity = 1.768e-6
Dispersion = 1e-8
reac = 1e-6

# concentration list
c = np.empty((len(length)))

# solving 1D transport equation 
for j in range(len(length)):
  if length[j] <= 0:
    c[j] = 1
  else: 
    c[j] = c0/2 * math.erfc((length[j] - velocity*time)/math.sqrt(4 * Dispersion * time)) * math.exp(-reac * length[j] / velocity)


source = ColumnDataSource(data = dict(x=length, y=c))

plot = Figure(min_height = 400, y_axis_label='c(t)/c0',
            x_axis_label='x [m]',sizing_mode="stretch_both")
plot.line('x', 'y', source = source, line_width = 3, line_alpha = 0.6, line_color = 'red')
plot.y_range = Range1d(0, 1.05)
plot.xaxis.axis_label_text_font_size = "17pt"
plot.yaxis.axis_label_text_font_size = "17pt"
plot.xaxis.major_label_text_font_size = "12pt"
plot.yaxis.major_label_text_font_size = "12pt" 

# initial slider parameters (min, max, step, value)
t = [np.log(3.6e1), np.log(1.2096e6), (np.log(1.2096e6)-np.log(3.6e1))/1000, np.log(21636)]
l = [0.01, 1, 0.01, 0.2]
r = [0.005, 0.5, 0.001, 0.05]
D = [np.log(1e-9), np.log(1e-7), (np.log(1e-7)-np.log(1e-9))/100, np.log(1e-8)]
d = [np.log(1e-8), np.log(1e-3), (np.log(1e-3)-np.log(1e-8))/100, np.log(1e-6)]
q = [1, 100, 1, 25]
n = [0.01, 1, 0.01, 0.5]

# sliders
t_sl = Slider(start=t[0], end=t[1], value=t[3], step=t[2], title="Time",
                    format=FuncTickFormatter(code="""return (Math.exp(tick)/3600).toFixed(2) +' [h]'"""),sizing_mode="stretch_width")
l_sl = Slider(title = "Column length", start = l[0], end = l[1], step = l[2], value = l[3],
                    format=FuncTickFormatter(code="""return tick.toFixed(2)+' [m]'"""),sizing_mode="stretch_width")
r_sl = Slider(title = "Column radius", start = r[0], end = r[1], step = r[2], value = r[3],
                    format=FuncTickFormatter(code="""return tick.toFixed(2)+' [m]'"""),sizing_mode="stretch_width")
D_sl = Slider(title = "Dispersion coefficient ", start = D[0], end = D[1], step = D[2], value =D[3],
                    format=FuncTickFormatter(code="""return Math.exp(tick).toExponential(1).toString()+' [m2/s]'"""),sizing_mode="stretch_width")
d_sl = Slider(title = "Reaction coefficient ", start = d[0], end = d[1], step = d[2], value = d[3],
                    format=FuncTickFormatter(code="""return Math.exp(tick).toExponential(1).toString()+' [1/s]'"""),sizing_mode="stretch_width")
q_sl = Slider(title = "Flow Rate", start = q[0], end = q[1], step = q[2], value = q[3],
                    format=FuncTickFormatter(code="""return tick.toFixed(0)+' [mL/h]'"""),sizing_mode="stretch_width")
n_sl = Slider(title = "Porosity", start = n[0], end = n[1], step = n[2], value = n[3],
                    format=FuncTickFormatter(code="""return tick.toFixed(2)+' [-]'"""),sizing_mode="stretch_width")

callback = CustomJS(args=dict(source=source,
                            t_sl = t_sl,
                            l_sl = l_sl,
                            d_sl = d_sl,
                            D_sl = D_sl,
                            r_sl = r_sl,
                            q_sl = q_sl,
                            n_sl = n_sl),
    code="""
    const data = source.data;
    const t = Math.exp(t_sl.value);
    const l = l_sl.value;
    const r = r_sl.value;
    const reac = Math.exp(d_sl.value);
    const D = Math.exp(D_sl.value);
    const q = q_sl.value;
    const n = n_sl.value;
    const x = data['x'] 
    const y = data['y']
    const c0 = 1;

    const A = math.PI * Math.pow(r,2);            
    const vel = q/(3.6*Math.pow(10,9)*n*A);       

    for (let j = 0; j < x.length; j++) {
      x[j] = -0.02*l + 1.02*l/x.length * j;
    }
    
    for (let i = 0; i < x.length; i++) {
      if (x[i] <= 0) {
        y[i] = 1;
      } else {
        y[i] = c0/2 * (1-math.erf((x[i] - vel*t)/(math.sqrt(4*D*t))))*math.exp(-reac*x[i]/vel);
    }}
    source.change.emit();
""")

savebutton = Button(label="Save", button_type="success",sizing_mode="stretch_width")
savebutton.js_on_click(CustomJS(args=dict(source=source),code=open(os.path.join(os.path.dirname(__file__),"download.js")).read()))
#credit: https://stackoverflow.com/questions/31824124/is-there-a-way-to-save-bokeh-data-table-content

# callbacks for widgets
t_sl.js_on_change('value', callback)
l_sl.js_on_change('value', callback)
r_sl.js_on_change('value', callback)
d_sl.js_on_change('value', callback)
D_sl.js_on_change('value', callback)
q_sl.js_on_change('value', callback)
n_sl.js_on_change('value', callback)


layout = column(t_sl,l_sl,r_sl,d_sl,D_sl,q_sl,n_sl,savebutton,sizing_mode="stretch_width")

tab1 = Panel(child=plot, title="ADRE")
plots = Tabs(tabs=[tab1])


# Work with template in order to modify html code
script, (div2, div1) = components((layout,plot))

# Add hmtl lines
f = open("./themodel.js", "w")
script = "\n".join(script.split("\n")[2:-1])
f.write(script)
f.close()

# read in the template file
with open('template', 'r') as file :
  filedata = file.read()

# replace the target strings (object in html is "placeholder")
filedata = filedata.replace('+placeholder1+', div1)
filedata = filedata.replace('+placeholder2+', div2)

# write to html file
with open('1D_column_test.html', 'w') as file:
  file.write(filedata)

