import wx
import os #needed to join paths in open/save
import threading
import copy #deep copy for filter

class mainwindow(wx.Frame):
    def __init__(self, parent, title):
        self.input = ['', '', '', '', '', ''] #Save user entered values
        self.dirname = ''
        self.filename = ''
        #Creating the window, setting it blue, and adding a text box to it
        wx.Frame.__init__(self, parent, title = title, size =(1000, 800))
        self.SetBackgroundColour((150, 200, 255)) #light blue
        self.logger = wx.TextCtrl(self, size=(300, 150),style=wx.TE_MULTILINE|\
                                  wx.TE_RICH)
        self.CreateStatusBar()
        self.Bind(wx.EVT_CLOSE, self.OnExit) #bind x button
        self.is_header = False #Input has header if True
        self.copy_header = False #copy header to output
        self.is_csv = False #Input is csv file
        self.want_csv = False #output should be csv file
        self.smart_check = False #control type of output based on input
        
        #Setting up the "File" menu option
        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", \
                                   "Open a Text File of Points to Interpolate")
        menuSave = filemenu.Append(wx.ID_SAVE, \
                                   "&Save", "Select a Text File for Output")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", \
                                    "Information About the Program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"&Exit","Terminate the Program")
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        #Setting up the "Help" menu option
        helpmenu = wx.Menu()
        self.menuHelp = helpmenu.Append(wx.ID_HELP, "&Help", \
                                   "Help on Using the Program")
        self.Bind(wx.EVT_MENU, self.OnHelp, self.menuHelp)


        #Creating File MenuBar
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(helpmenu, "&Help")
        self.SetMenuBar(menubar)

        #Create Sizers 
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=7, vgap=3)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)

        #Input File Box
        self.input_text = wx.StaticText(self, label = "Input File Name:")
        self.input_box = wx.TextCtrl(self, value="", \
                                      size = (200, -1))
        grid.Add(self.input_text, pos = (0, 0))
        grid.Add(self.input_box, pos = (1, 0))
        self.Bind(wx.EVT_TEXT, lambda x: self.EvtText(x, 0), \
                  self.input_box)
        self.make_bold(self.input_text)
        self.make_bold(self.input_box)

        #Input Browse Button
        self.browse_button_input = wx.Button(self, label = "Browse..")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.browse_button_input)
        self.make_bold(self.browse_button_input)
        grid.Add(self.browse_button_input, pos = (2, 0))

        #Output File Box
        self.output_text = wx.StaticText(self, label = "Output File Name:")
        self.output_box = wx.TextCtrl(self, value="", \
                                      size = (200, -1))
        grid.Add(self.output_text, pos = (0, 1))
        grid.Add(self.output_box, pos = (1, 1))
        self.Bind(wx.EVT_TEXT, lambda x: self.EvtText(x, 1), \
                  self.output_box)
        self.make_bold(self.output_text)
        self.make_bold(self.output_box)

        #Browse Button Output
        self.browse_button_out = wx.Button(self, label = "Browse..")
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.browse_button_out)
        self.make_bold(self.browse_button_out)
        grid.Add(self.browse_button_out, pos = (2, 1))

        #Number of Lines
        self.num_lines_prompt = wx.StaticText(\
            self,label="Number of lines: ")
        self.num_lines = wx.TextCtrl(self, value="", \
                                      size = (200, -1))
        grid.Add(self.num_lines_prompt, pos = (3, 0))
        grid.Add(self.num_lines, pos = (4, 0))
        self.Bind(wx.EVT_TEXT, lambda x: self.EvtText(x, 4), self.num_lines)
        self.make_bold(self.num_lines)
        self.make_bold(self.num_lines_prompt)

        #Filter
        self.filter_prompt = wx.StaticText(\
            self,label="Filter: ")
        self.filter = wx.TextCtrl(self, value="", \
                                      size = (200, -1))
        grid.Add(self.filter_prompt, pos = (3, 1))
        grid.Add(self.filter, pos = (4, 1))
        self.Bind(wx.EVT_TEXT, lambda x: self.EvtText(x, 5), self.filter)
        self.make_bold(self.filter_prompt)
        self.make_bold(self.filter)

        #Input format
        self.in_format_prompt = wx.StaticText(self,label="Input File Format: ")
        self.in_format = wx.TextCtrl(self, value="", \
                                      size = (200, -1))
        grid.Add(self.in_format_prompt, pos = (5, 0))
        grid.Add(self.in_format, pos = (6, 0))
        self.Bind(wx.EVT_TEXT, lambda x: self.EvtText(x, 2), self.in_format)
        self.make_bold(self.in_format_prompt)
        
        #Output Format
        self.out_format_prompt= wx.StaticText(self,label="Output File Format: ")
        self.out_format = wx.TextCtrl(self, value="", \
                                      size = (200, -1))
        grid.Add(self.out_format_prompt, pos = (5, 1))
        grid.Add(self.out_format, pos = (6, 1))
        self.Bind(wx.EVT_TEXT, lambda x: self.EvtText(x, 3), self.out_format)
        self.make_bold(self.out_format_prompt)

        #Has Header Checkbox
        self.header_check = wx.CheckBox(self, style=wx.CHK_2STATE, \
                                    name = "Has Header")
        grid.Add(self.header_check, pos = (7, 1))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckHead, self.header_check)
        self.header_check_lbl = wx.StaticText(self, label =\
                                              ("                               "\
                                              + "              Has Header"))
        grid.Add(self.header_check_lbl, pos=(7, 0))
        self.make_bold(self.header_check_lbl)

        #Copy Header Checkbox
        self.header_copy = wx.CheckBox(self, style=wx.CHK_2STATE, \
                                    name = "Copy Header")
        grid.Add(self.header_copy, pos = (8, 1))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCopy, self.header_copy)
        self.header_copy_lbl = wx.StaticText(self, label =\
                                             ("                               " +\
                                             "            Copy Header"))
        grid.Add(self.header_copy_lbl, pos=(8, 0))
        self.make_bold(self.header_copy_lbl)
        self.header_copy.Enable(False)

        #Input is CSV Checkbox
        self.in_is_csv = wx.CheckBox(self, style=wx.CHK_2STATE, \
                                    name = "Input File CSV")
        grid.Add(self.in_is_csv, pos = (9, 1))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCSV, self.in_is_csv)
        self.in_is_csv_lbl = wx.StaticText(self, label =\
                                             ("                               " +\
                                             "      Input is CSV File"))
        grid.Add(self.in_is_csv_lbl, pos=(9, 0))
        self.make_bold(self.in_is_csv_lbl)
        
        #Output is CSV Checkbox
        self.out_is_csv = wx.CheckBox(self, style=wx.CHK_2STATE, \
                                    name = "Output File CSV")
        grid.Add(self.out_is_csv, pos = (10, 1))
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckOut, self.out_is_csv)
        self.out_is_csv_lbl = wx.StaticText(self, label =\
                                             ("                               " +\
                                             "   Output is CSV File"))
        grid.Add(self.out_is_csv_lbl, pos=(10, 0))
        self.make_bold(self.out_is_csv_lbl)

        if self.smart_check:
            self.out_is_csv.Enable(False)

        #Smart Checkbox
        create_smartcheck = filemenu.Append(wx.ID_ANY, "Smart&Check", "SmartCheck", wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.OnSmartCheck, create_smartcheck)

        #Convert Button
        self.convert_button = wx.Button(self, label="Convert")
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.convert_button)
        self.make_bold(self.convert_button)

        #Clear Button
        self.clear_button = wx.Button(self, label = "Clear")
        self.Bind(wx.EVT_BUTTON, self.Clear, self.clear_button)
        self.make_bold(self.clear_button)

        #Setup sizers and place them
        hSizer.AddSpacer(10)
        hSizer.Add(grid, 0, wx.EXPAND, 10)
        hSizer.AddSpacer(10)
        hSizer.Add(self.logger, 1, wx.EXPAND)
        mainSizer.AddSpacer(10)
        mainSizer.Add(hSizer, 1,wx.EXPAND)
        mainSizer.AddSpacer(10)
        mainSizer.Add(self.convert_button, 0, wx.EXPAND | wx.CENTER)
        mainSizer.AddSpacer(5)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.clear_button, 1, wx.LEFT)
        mainSizer.Add(buttonSizer, 0)
        self.SetSizerAndFit(mainSizer)
        self.Centre()


    def OnAbout(self, e): #Basic info about software
        '''Displays a pupup box that gives information about this software'''
        dlg = wx.MessageDialog(self, "Convert Text File Software " + \
                               "\n\nThis Graphical-" +\
                               "User-Interface for converting between " +\
                               "Space separated and comma separated text files"\
                               + " was created by" +\
                               " Cameron Buttazzoni for research " + \
                               "purposes at the Fires Management " +\
                               "System Laboratory in the Faculty of Forestry"+\
                               " at the University of Toronto\n\n" +\
                               "THIS SOFTWARE IS NOT VALIDATED OR CERTIFIED" +\
                               " FOR OPERATIONAL USE"\
                               + "\nCopyright: Cameron Buttazzoni\n\n", \
                               "About Convert Text Files Software", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnExit(self, e):  #exit
        '''Exit the software'''
        self.Close(True)
        raise SystemExit
        
    def OnSave(self, e): #Same functionality as browse output file
        '''Select an output file'''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, \
                            "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.input[1] = os.path.join(self.dirname, self.filename)
            self.output_box.SetValue(os.path.join(self.dirname, self.filename))
        dlg.Destroy()

    def OnOpen(self, e): #same functionality as browse input file
        '''Open an input file'''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, \
                            "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.input[0] = os.path.join(self.dirname, self.filename)
            self.input_box.SetValue(os.path.join(self.dirname, self.filename))
        dlg.Destroy()

    def OnHelp(self, e): #brief tutorial on commands + how to use
        '''Opens a box displaying this on help'''
        help_text = '''Input file should be a space seperated or csv file\n
For input format, leave it blank to copy all of the values from the input file\n
Instead, you can enter comma or space seperated numbers to choose from specific
input columns that you want to include.\nFor output format, the format is
the same, but this chooses the order the inputs will be placed in the output
file. Leave this field blank to copy all inputs.\n Numbers not entered will
be replaced by NULL for space seperated output files, and an empty string
for CVS output files.\n WARNING: Reordering the output DOES NOT reorder the
header if you select to copy it.\nSmartCheck Automatically converts to a
space seperated file if the input is CSV, and vice versa.\n
Number of lines copies up to that many lines (not counting the header if copied
\nTo use filter, enter the values as column number (starting from 1)::string\n
* can be included so to filter such that everything else must be in any string.
-- can be included at the start of a string to copy all but those ones.
% Can be included in a string to represent any character (even none)\n
Separate additional filters with a comma without a space, example:\n
4::196*,3::--Type1,1::1%%%
This would filter everything such that the 4th column must include 196
somewhere. the 3rd column cannot be Type1 and the 1st column must be a number
in the one thousands.'''
        help_dlg = wx.MessageDialog(self, help_text, "File Conversion" +\
                                    " Software Help", wx.OK)
        help_dlg.ShowModal()
        help_dlg.Destroy()

    def EvtText(self, e, num):
        '''Entering text sets input to new entered value'''
        try:
            value = e.GetString().encode('ascii', 'ignore')
        except AttributeError:
            pass
        if num == 2: #input format
            if value == '':
                self.input[num] = ''
            elif len(value.split(',')) != 1:
                temp_list = value.split(',')
                for x in range(len(temp_list)):
                    try:
                        if temp_list[x] != '' and temp_list[x] != ' ':
                            temp_list[x] = int(temp_list[x])
                    except (ValueError, IndexError):
                        self.logger.AppendText("\nInvalid Format\n")
                self.input[num] = temp_list
            else:
                temp_list = value.split()
                for x in range(len(temp_list)):
                    try:
                        if temp_list[x] != '' and temp_list[x] != ' ':
                            temp_list[x] = int(temp_list[x])
                    except ValueError:
                        self.logger.AppendText("\nInvalid Format\n")
                self.input[num] = temp_list
        elif num == 3: #output format
            if value == '':
                self.input[num] = ''
            elif len(value.split(',')) != 1:
                temp_list = value.split(',')
                for x in range(len(temp_list)):
                    try:
                        if temp_list[x] != '' and temp_list[x] != ' ':
                            temp_list[x] = int(temp_list[x])
                    except ValueError:
                        self.logger.AppendText("\nInvalid Format\n")
                self.input[num] = temp_list
            else:
                temp_list = value.split()
                for x in range(len(temp_list)):
                    try:
                        if temp_list[x] != '' and temp_list[x] != ' ':
                            temp_list[x] = int(temp_list[x])
                    except ValueError:
                        self.logger.AppendText("\nInvalid Format\n")
                self.input[num] = temp_list
        elif num == 5: #Filter
            temp_list = value.split(',')
            for x in range(len(temp_list)):
                try:
                    temp_list[x] = temp_list[x].split('::')
                    temp_list[x][0] = int(temp_list[x][0])
                    if type(temp_list[x][1]) != str:
                        raise ValueError
                except (ValueError, IndexError, TypeError):
                    pass
            self.input[5] = temp_list
        else:
            self.input[num] = value

    def Clear(self, e): #clears logger and all entered values
        self.logger.Clear()
        self.input_box.Clear()
        self.output_box.Clear()
        self.out_format.Clear()
        self.in_format.Clear()
        self.filter.Clear()
        self.num_lines.Clear()
        for x in range(len(self.input)):
            self.input[x] = ''

    def OnClick(self, e):
        '''Convert'''
        self.disable_buttons()
        if self.input[2] == '': #Copy everything
            copy_all_thread = threading.Thread(target = self.copy_all)
            copy_all_thread.setDaemon(True)
            copy_all_thread.start()
        else: #Copy some
            copy_select_thread = threading.Thread(target = self.copy_select)
            copy_select_thread.setDaemon(True)
            copy_select_thread.start()


    def copy_all(self):
        #Copy Everything Over
        try:
            in_file = open(self.input[0], 'r')
        except IOError:
            self.logger.AppendText("\nInvalid Input File\n\n")
            self.enable_buttons()
            return
        try:
            out_file = open(self.input[1], 'w')
        except IOError:
            self.logger.AppendText("\nInvalid Output File\n\n")
            self.enable_buttons()
            return
        temp = ''
        if self.is_header:
            temp = in_file.readline()
        temp = in_file.readline()
        if self.is_csv:
            find_length_in = len(temp.split(','))
        else:
            find_length_in = len(temp.split())
        try:
            if max(self.input[2]) > find_length_in:
                in_file.close()
                out_file.close()
                self.logger.AppendText("\nInput Format Value Too Large\n\n")
                self.enable_buttons()
                return
        except ValueError:
            pass
        in_file.seek(0)
        self.logger.AppendText("\nConverting...\n\n")
        if self.is_header: #Copy header
            temp = in_file.readline()
            if temp[-1] == '\n':
                temp = temp[:-1]
            if self.copy_header:
                if self.is_csv:
                    temp2 = temp.split(',')
                    for x in range(len(temp2)):
                        if not self.want_csv:
                            if temp2[x] != '':
                                if x != len(temp2) - 1:
                                    out_file.write(temp2[x] + " ")
                                else:
                                    out_file.write(temp2[x])
                            else:
                                if x != len(temp2) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                        else:
                            if x != len(temp2) - 1:
                                out_file.write(temp2[x] + ",")
                            else:
                                out_file.write(temp2[x])
                    out_file.write('\n')
                else:
                    temp2 = temp.split()
                    for x in range(len(temp2)):
                        if self.want_csv:
                            if x != len(temp2) - 1:
                                out_file.write(temp2[x] + ",")
                            else:
                                out_file.write(temp2[x])
                        else:
                            if temp2[x] != '':
                                if x != len(temp2) - 1:
                                    out_file.write(temp2[x] + " ")
                                else:
                                    out_file.write(temp2[x])
                            else:
                                if x != len(temp2) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                    out_file.write('\n')
        temp = in_file.readline()
        if self.input[3] == '': #if no output changes
            count = 1
            while temp != '':
                if temp[-1] == '\n':
                    temp = temp[:-1]
                if self.is_csv:
                    temp2 = temp.split(',')
                    check = self.filter_line(temp2)
                    if check == -1:
                        self.logger.AppendText("Invalid Filter Inputted")
                        self.enable_buttons()
                        return
                    elif check == 0:
                        temp = in_file.readline()
                        continue
                    for x in range(len(temp2)):
                        if not self.want_csv:
                            if temp2[x] != '':
                                if x != len(temp2) - 1:
                                    out_file.write(temp2[x] + " ")
                                else:
                                    out_file.write(temp2[x])
                            else:
                                if x != len(temp2) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                        else:
                            if x != len(temp2) - 1:
                                out_file.write(temp2[x] + ',')
                            else:
                                out_file.write(temp2[x])
                    out_file.write('\n')
                else:
                    temp2 = temp.split()
                    check = self.filter_line(temp2)
                    if check == -1:
                        self.logger.AppendText("Invalid Filter Inputted")
                        self.enable_buttons()
                        return
                    elif check == 0:
                        temp = in_file.readline()
                        continue
                    for x in range(len(temp2)):
                        if self.want_csv:
                            if x != len(temp2) - 1:
                                out_file.write(temp2[x] + ",")
                            else:
                                out_file.write(temp2[x])
                        else:
                            if temp2[x] != '':
                                if x != len(temp2) - 1:
                                    out_file.write(temp2[x] + " ")
                                else:
                                    out_file.write(temp2[x])
                            else:
                                if x != len(temp2) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                    out_file.write('\n')
                temp = in_file.readline()
                try:
                    if self.input[4] != '' and count >= int(self.input[4]):
                        break
                    count += 1
                except ValueError:
                    self.logger.AppendText("\nInvalid number of runs\n\n")
                    return
            in_file.close()
            out_file.close()
            self.enable_buttons()
            self.logger.AppendText("\nFinished Conversion\n\n")
            return
        count = 1
        while temp != '': #if output formatting
            for x in range(len(self.input[3])):
                if type(self.input[3][x]) != int:
                    self.logger.AppendText("\nInvalid Output Format\n\n")
                    self.enable_buttons()
                    return
            if temp[-1] == '\n':
                temp = temp[:-1]
            if self.is_csv:
                temp2 = temp.split(',')
                check = self.filter_line(temp2)
                if check == -1:
                    self.logger.AppendText("Invalid Filter Inputted")
                    self.enable_buttons()
                    return
                elif check == 0:
                    temp = in_file.readline()
                    continue
                new_line = ["NULL"] * max(self.input[3])
                for x in range(len(temp2)):
                    try:
                        new_line[self.input[3][x] - 1] = temp2[x] #first spot is 1
                    except IndexError:
                        pass
                for x in range(len(new_line)):
                    if not self.want_csv:
                        if new_line[x] != '':
                            if x != len(new_line) - 1:
                                out_file.write(new_line[x] + " ")
                            else:
                                out_file.write(new_line[x])
                        else:
                            if x != len(new_line) - 1:
                                out_file.write("NULL ")
                            else:
                                out_file.write("NULL")
                    else:
                        if x != len(new_line) - 1:
                            out_file.write(new_line[x] + ",")
                        else:
                            out_file.write(new_line[x])
                out_file.write('\n')
            else:
                temp2 = temp.split()
                check = self.filter_line(temp2)
                if check == -1:
                    self.logger.AppendText("Invalid Filter Inputted")
                    self.enable_buttons()
                    return
                elif check == 0:
                    temp = in_file.readline()
                    continue
                new_line = [""] * max(self.input[3])
                for x in range(len(temp2)):
                    try:
                        new_line[self.input[3][x] - 1] = temp2[x] #first spot is 1
                    except IndexError:
                        pass
                for x in range(len(new_line)):
                    if self.want_csv:
                        if x != len(new_line) - 1:
                            out_file.write(new_line[x] + ",")
                        else:
                            out_file.write(new_line[x])
                    else:
                        if new_line[x] != '':
                            if x != len(new_line) - 1:
                                out_file.write(new_line[x] + " ")
                            else:
                                out_file.write(new_line[x])
                        else:
                            if x != len(new_line) - 1:
                                out_file.write("NULL ")
                            else:
                                out_file.write("NULL")
                out_file.write('\n')
            temp = in_file.readline()
            try:
                if self.input[4] != '' and count >= int(self.input[4]):
                    break
                count += 1
            except ValueError:
                self.logger.AppendText("\nInvalid number of runs\n\n")
                return
        in_file.close()
        out_file.close()
        self.enable_buttons()
        self.logger.AppendText("\nFinished Conversion\n\n")
        return
                    

    def copy_select(self):
        '''Copy some of input to output file'''
        for x in range(len(self.input[2])):
            if type(self.input[2][x]) != int and ':' not in self.input[2][x]:
                self.logger.AppendText("\nInvalid Input Format\n\n")
                self.enable_buttons()
                return
        try:
            in_file = open(self.input[0], 'r')
        except IOError:
            self.logger.AppendText("\nInvalid Input File\n\n")
            self.enable_buttons()
            return
        try:
            out_file = open(self.input[1], 'w')
        except IOError:
            self.logger.AppendText("\nInvalid Output File\n\n")
            self.enable_buttons()
            return
        temp = ''
        if self.is_header:
            temp = in_file.readline()
        temp = in_file.readline()
        if self.is_csv:
            find_length_in = len(temp.split(','))
        else:
            find_length_in = len(temp.split())
        try:
            if max(self.input[2]) > find_length_in:
                in_file.close()
                out_file.close()
                self.logger.AppendText("\nInput Format Value Too Large\n\n")
                self.enable_buttons()
                return
        except ValueError:
            pass
        in_file.seek(0)
        self.logger.AppendText("\nConverting...\n\n")
        if self.is_header: #copy header file
            temp = in_file.readline()
            if temp[-1] == '\n':
                temp = temp[:-1]
            if self.copy_header:
                if self.is_csv:
                    temp2 = temp.split(',')
                    for x in range(len(temp2)):
                        if not self.want_csv:
                            if temp2[x] != '':
                                if x != len(temp2) - 1:
                                    out_file.write(temp2[x] + " ")
                                else:
                                    out_file.write(temp2[x])
                            else:
                                if x != len(temp2) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                        else:
                            if x != len(temp2) - 1:
                                out_file.write(temp2[x] + ",")
                            else:
                                out_file.write(temp2[x])
                    out_file.write('\n')
                else:
                    temp2 = temp.split()
                    for x in range(len(temp2)):
                        if self.want_csv:
                            if x != len(temp2) - 1:
                                out_file.write(temp2[x] + ",")
                            else:
                                out_file.write(temp2[x])
                        else:
                            if temp2[x] != '':
                                if x != len(temp2) - 1:
                                    out_file.write(temp2[x] + " ")
                                else:
                                    out_file.write(temp2[x])
                            else:
                                if x != len(temp2) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                    out_file.write('\n')
        temp = in_file.readline()
        #Copy selected ones over
        count = 1
        if self.input[3] == '': #if no output formatting
            while temp != '':
                if temp[-1] == '\n':
                    temp = temp[:-1]
                if self.is_csv:
                    temp2 = temp.split(',')
                    check = self.filter_line(temp2)
                    if check == -1:
                        self.logger.AppendText("Invalid Filter Inputted")
                        self.enable_buttons()
                        return
                    elif check == 0:
                        temp = in_file.readline()
                        continue
                    for x in range(len(self.input[2])):
                        if not self.want_csv:
                            if temp2[self.input[2][x] - 1] != '':
                                if x != len(self.input[2]) - 1:
                                    out_file.write(temp2[self.input[2][x] - 1] + " ")
                                else:
                                    out_file.write(temp2[self.input[2][x] - 1])
                            else:
                                if x != len(self.input[2]) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                        else:
                            if x != len(self.input[2]) - 1:
                                out_file.write(temp2[self.input[2][x] - 1] + ",")
                            else:
                                out_file.write(temp2[self.input[2][x] - 1])
                    out_file.write('\n')
                else:
                    temp2 = temp.split()
                    check = self.filter_line(temp2)
                    if check == -1:
                        self.logger.AppendText("Invalid Filter Inputted")
                        self.enable_buttons()
                        return
                    elif check == 0:
                        temp = in_file.readline()
                        continue
                    for x in range(len(self.input[2])):
                        if self.want_csv:
                            if x != len(self.input[2]) - 1:
                                out_file.write(temp2[self.input[2][x] - 1] + ",")
                            else:
                                out_file.write(temp2[self.input[2][x] - 1])
                        else:
                            if temp2[self.input[2][x] - 1] != '':
                                if x != len(self.input[2]) - 1:
                                    out_file.write(temp2[self.input[2][x] - 1] + " ")
                                else:
                                    out_file.write(temp2[self.input[2][x] - 1])
                            else:
                                if x != len(self.input[2]) - 1:
                                    out_file.write("NULL ")
                                else:
                                    out_file.write("NULL")
                    out_file.write('\n')
                temp = in_file.readline()
                try:
                    if self.input[4] != '' and count >= int(self.input[4]):
                        break
                    count += 1
                except ValueError:
                    self.logger.AppendText("\nInvalid number of runs\n\n")
                    return
            in_file.close()
            out_file.close()
            self.enable_buttons()
            self.logger.AppendText("\nFinished Conversion\n\n")
            return

        while temp != '': #if output formatting
            for x in range(len(self.input[3])):
                if type(self.input[3][x]) != int:
                    self.logger.AppendText("\nInvalid Output Format\n\n")
                    self.enable_buttons()
                    return
            if temp[-1] == '\n':
                temp = temp[:-1]
            if self.is_csv:
                temp2 = temp.split(',')
                check = self.filter_line(temp2)
                if check == -1:
                    self.logger.AppendText("Invalid Filter Inputted")
                    self.enable_buttons()
                    return
                elif check == 0:
                    temp = in_file.readline()
                    continue
                new_line = ["NULL"] * max(self.input[3])
                for x in range(len(temp2)):
                    try:
                        new_line[self.input[3][x] - 1] = \
                                                  temp2[self.input[2][x] - 1]
                        #first spot is 1
                    except IndexError:
                        try:
                            new_line.append(temp2[self.input[2][x] - 1])
                        except IndexError:
                            pass
                for x in range(len(new_line)):
                    if not self.want_csv:
                        if new_line[x] != '':
                            if x != len(new_line) - 1:
                                out_file.write(new_line[x] + " ")
                            else:
                                out_file.write(new_line[x])
                        else:
                            if x != len(new_line) - 1:
                                out_file.write("NULL ")
                            else:
                                out_file.write("NULL")
                    else:
                        if x != len(new_line) - 1:
                            out_file.write(new_line[x] + ",")
                        else:
                            out_file.write(new_line[x])
                out_file.write('\n')
            else:
                temp2 = temp.split()
                check = self.filter_line(temp2)
                if check == -1:
                    self.logger.AppendText("Invalid Filter Inputted")
                    self.enable_buttons()
                    return
                elif check == 0:
                    temp = in_file.readline()
                    continue
                new_line = [""] * max(self.input[3])
                for x in range(len(temp2)):
                    try:
                        new_line[self.input[3][x] - 1] = \
                                                  temp2[self.input[2][x] - 1]
                        #first spot is 1
                    except IndexError:
                        try:
                            new_line.append(temp2[self.input[2][x] - 1])
                        except IndexError:
                            pass
                for x in range(len(new_line)):
                    if self.want_csv:
                        if x != len(new_line) - 1:
                            out_file.write(new_line[x] + ",")
                        else:
                            out_file.write(new_line[x])
                    else:
                        if new_line[x] != '':
                            if x != len(new_line) - 1:
                                out_file.write(new_line[x] + " ")
                            else:
                                out_file.write(new_line[x])
                        else:
                            if x != len(new_line) - 1:
                                out_file.write("NULL ")
                            else:
                                out_file.write("NULL")
                out_file.write('\n')
            temp = in_file.readline()
            try:
                if self.input[4] != '' and count >= int(self.input[4]):
                    break
                count += 1
            except ValueError:
                self.logger.AppendText("\nInvalid number of runs\n\n")
                return
        in_file.close()
        out_file.close()
        self.enable_buttons()
        self.logger.AppendText("\nFinished Conversion\n\n")
        return
            
    def filter_line(self, line):
        '''Checks if line passes filter'''
        if self.input[5]=='' or self.input[5]==[''] or self.input[5] == [['']]:
            return 1
        for x in range(len(self.input[5])):
            temp = copy.deepcopy(self.input[5])
            try:
                if '*' in temp[x][1] and '--' in temp[x][1]:
                    temp[x][1] = temp[x][1].translate(None, "*")
                    temp[x][1] = temp[x][1].translate(None, "--")
                    if temp[x][1] in line[self.input[5][x][0]-1]:
                        return 0
                elif '*' in temp[x][1]:
                    temp[x][1] = temp[x][1].translate(None, "*")
                    if temp[x][1] not in line[self.input[5][x][0]-1]:
                        return 0
                elif '%' in temp[x][1] and '--' in temp[x][1]:
                    temp[x][1] = temp[x][1].translate(None, "--")
                    if len(temp[x][1]) == len(line[self.input[5][x][0]-1]):
                        flag = True
                        for y in range(len(temp[x][1])):
                            if temp[x][1][y] != line[self.input[5][x][0]-1][y]\
                               and temp[x][1][y] != '%':
                                flag = False
                                break
                        if flag:
                            return 0
                elif '%' in temp[x][1]:
                    if len(temp[x][1]) != len(line[self.input[5][x][0]-1]):
                        return 0
                    for y in range(len(temp[x][1])):
                        if temp[x][1][y] != line[self.input[5][x][0]-1][y]\
                               and temp[x][1][y] != '%':
                                return 0
                elif '--' == temp[x][1][:2]:
                    temp[x][1] = temp[x][1].translate(None, "--")
                    if line[self.input[5][x][0] - 1] == temp[x][1]:
                        return 0
                else:
                    if line[self.input[5][x][0] - 1] != temp[x][1]:
                        return 0
            except IndexError:
                return -1
        return 1
    def make_bold(self, text):
        '''Makes prompts and button text bold'''
        temp_font = text.GetFont()
        temp_font.SetWeight(wx.BOLD)
        text.SetFont(temp_font)

    def disable_buttons(self):
        '''Prevent User from clicking any buttons'''
        self.convert_button.Enable(False)
        self.clear_button.Enable(False)
        self.browse_button_out.Enable(False)
        self.browse_button_input.Enable(False)

    def enable_buttons(self):
        '''Reenable buttons to be pressed'''
        self.convert_button.Enable(True)
        self.clear_button.Enable(True)
        self.browse_button_out.Enable(True)
        self.browse_button_input.Enable(True)

    def OnCheckHead(self, e):
        if self.is_header == False:
            self.is_header = True
        else:
            self.is_header = False
        if self.header_copy.IsEnabled():
            self.header_copy.Enable(False)
        else:
            self.header_copy.Enable(True)

    def OnCheckCopy(self, e):
        if self.copy_header:
            self.copy_header = False
        else:
            self.copy_header = True
            
    def OnCheckCSV(self, e):
        if self.is_csv:
            self.is_csv = False
            if self.smart_check:
                self.want_csv = True
                self.out_is_csv.SetValue(True)
        else:
            self.is_csv = True
            if self.smart_check:
                self.want_csv = False
                self.out_is_csv.SetValue(False)
            
    def OnCheckOut(self, e):
        if self.want_csv:
            self.want_csv = False
        else:
            self.want_csv = True

    def OnSmartCheck(self, e):
        if self.smart_check:
            self.smart_check = False
            self.out_is_csv.Enable(True)
        else:
            self.smart_check = True
            self.out_is_csv.Enable(False)

#run the GUI
app = wx.App(False)
frame = mainwindow(None, "Fire Interpolation System")
frame.Show()
app.MainLoop()
