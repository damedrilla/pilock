from RPLCD import CharLCD
lcd = CharLCD()
lcd.write_string(u'Raspberry Pi HD44780')
lcd.cursor_pos = (2, 0)
lcd.write_string(u'http://github.com/\n\rdbrgn/RPLCD')