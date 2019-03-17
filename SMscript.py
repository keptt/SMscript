import email, smtplib, ssl, os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

def del_whitespaces(string):
    string = list(string);
    for i in range(len(string) - 1, -1, -1):
        if string[i] in "\n\v\t ":
             del string[i];
        else:
            break;
    for i in range(0, len(string), 1):
        if string[i] in "\n\v\t ":
            del string[i];
        else:
            break;   
    string = ''.join(string);
    return string;

def get_filename(filepath):
    filename = "";
    for i in range(len(filepath)-1, -1, -1):
        if filepath[i] == '\\':
            break;
        filename += filepath[i];
    return filename[-1::-1];        

def decode_binary_string(s):
    return ''.join(chr(int(s[i*8:i*8+8],2)) for i in range(len(s)//8));

def send_email_with_attached_file(port, host, username, password, from_, to_arr, subject, text, filepaths):
    count = 0;
    context = ssl.create_default_context();
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo();
        server.starttls(context = context);
        server.ehlo();
        server.login(username, password);
    except Exception as e:
        print(e);

    for i in range(0,len(to_arr)):

        message = MIMEMultipart();
        message["From"] = from_;
        message["To"] = to_arr[i];
        message["Subject"] = subject;
        message["Bcc"] = to_arr[i];

        message.attach(MIMEText(text, "plain", "utf-8"));

        for file in filepaths:

            filename_ = get_filename(file); #this cuts (if needed) filename from filepath stored in file
            
            with open(file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream");
                part.set_payload(attachment.read());

            encoders.encode_base64(part);

            part.add_header(
                "Content-Disposition",
                u"attachment", filename = (Header(filename_, 'utf-8').encode())
            );

            message.attach(part);
            
        email_text = message.as_string();

        try:
            server.sendmail(from_, to_arr[i], email_text);
        except Exception as e:
            print(e);
        else:
            count += 1;
            print (f"{count} letter is sent\n",);
    server.quit();
    print (f"finalle!\n(Overall number of sent emails is {count} out of {len(to_arr)})");
    
    
def read_smconfig(file):
    with open(file, "r") as f:
        buf = "";
        receivers = []; filepaths = [];
        text = "";
        port = 0; host = ""; username = ""; password = ""; subject = ""; from_ = "";

        for line in f:
            if (line =="\n" and "--TEXT" not in buf) or del_whitespaces(line) == "{":
                continue;
            if buf == "":
                pass;
            elif "--PORT" in buf:
                port = del_whitespaces(line);
                buf = "";
                continue;
            elif "--HOST" in buf:
                host = del_whitespaces(line);
                buf = "";
                continue;
            elif "--USERNAME" in buf:
                username = del_whitespaces(line);
                buf = "";
                continue;
            elif "--PASSWORD" in buf:
                password = del_whitespaces(line);
                buf = "";
                continue;
            elif "--SUBJECT" in buf:
                subject = del_whitespaces(line);
                buf = "";
                continue;
            elif "--TEXT" in buf:
                if del_whitespaces(line) != "}":
                    text += line;
                else:
                    buf = "";
                continue;
            elif "--FILEPATHS" in buf:
                if del_whitespaces(line) != "}":
                    filepaths.append(del_whitespaces(line));
                else:
                    buf = "";
                continue;
            elif "--SENDER" in buf:
                from_ = del_whitespaces(line);
                buf = "";
                continue;
            elif "--RECEIVERS" in buf:
                if del_whitespaces(line) != "}":
                    receivers.append(del_whitespaces(line));
                continue;

            if "--PORT" in line:
                buf = line;
            elif "--HOST" in line:
                buf = line;
            elif "--USERNAME" in line:
                buf = line;
            elif "--PASSWORD" in line:
                buf = line;
                continue;
            elif "--SUBJECT" in line:
                buf = line;
            elif "--TEXT" in line:
                buf = line;
            elif "--FILEPATHS" in line:
                buf = line;
            elif "--SENDER" in line:
                buf = line;
            elif "--RECEIVERS":
                buf = line;
        return ({
            "Port" : port,
            "Host" : host,
            "Username" : username,
            "Password" : password,
            "Subject" : subject,
            "Text" : text,
            "From" : from_,
            "Receivers" : receivers,
            "Filepaths" : filepaths
            })
#main#
answer = input("Are you sure you want to send mails? [y/n]: ");
filename = "smconfig.txt";

d = read_smconfig(filename);

while True:
    if answer == 'y' or answer == 'Y':
        filename = "smconfig.txt";      
        d = read_smconfig(filename);
        send_email_with_attached_file(d["Port"], d["Host"], d["Username"], decode_binary_string(d["Password"]), d["From"], d["Receivers"], d["Subject"], d["Text"], d["Filepaths"]);
        break;
    elif answer == 'n' or answer == 'N':
        break;
    else:
        answer = input("Input 'y' or 'n' in either lower or upper case: ");

