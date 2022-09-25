# UoL-ics-file-generator
[🇨🇳中文说明文档](https://github.com/YunfangHou/UoL-ics-file-generator/blob/main/README-cn.md)

Automatically generate an .ics file of University of Liverpool [Timetable](https://timetables.liverpool.ac.uk).

Please star the repo if you like it 🌟

## Usage
1. Download the newly released executable application.
2. Run the application.
3. Input your UoL student account username and password, the start year and end year of your academic year according to the instruction in the program window.
4. Find the file `timetable.ics` in the same folder of the application.
5. Import `timetable.ics` into your calendar app.

 macOS user attention: the `timetable.ics` will be saved in the user directory like `/Users/your_user_name/timetable.ics`, not the folder of the application.

## FAQ
### Q: Is there any application with a user interface?
A: There is no modern user interface with bottons. Only console app.

### Q: Is network needed?
A: Yes. The application need to read the timetable information from the Uol website.

### Q: Is my personal information secure? Can you get my password?
A: Your personal information is secure. This program just run on your own computer and nobody could get your password. Check the code if you like.

## TODO
- Language option
- Modern user interface
- Fix the file saving bug on macOS
