
## add your signals here
## For exmple:
## add simple bit signals
# gtkwave::addSignalsFromList { random-bit1 random-bit2 }
## add 32bits values with hex display
# gtkwave::addSignalsFromList { random-val1\[31:0\] }
## display random-val2 with analog display
# gtkwave::addSignalsFromList { random-val2\[31:0\] }
# gtkwave::/Edit/Data_Format/Analog/Step

#unhighlight signals
gtkwave::/Edit/UnHighlight_All

#set a nice zoom
gtkwave::setZoomFactor -10

#start with dynamic on
gtkwave::/View/Partial_VCD_Dynamic_Zoom_To_End

