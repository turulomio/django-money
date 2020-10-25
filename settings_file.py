from sys import path as sys_path
sys_path.append("money/reusing")
from text_inputs import input_string, input_YN
from myconfigparser import MyConfigParser

if __name__ == "__main__":
    print("Hidden settings are going to be generated in /etc/django_money/settings.conf")
    config=MyConfigParser("/etc/django_money/settings.conf")

    ans=input_YN("Do you want to change database settings?")
    if ans is True:
        ans = input_string("Add you database server", "127.0.0.1")
        config.set("db", "server", ans)
        ans = input_string("Add you database port", "5432")
        config.set("db", "port", ans)
        ans = input_string("Add your database name", "mylibrary")
        config.set("db", "db", ans)
        ans = input_string("Add you database user", "postgres")
        config.cset("db", "user", ans)
        ans = input_string("Add you database password", "your_pass")
        config.cset("db", "password", ans)

    ans=input_YN("Do you want to change smtp mail server settings?")
    if ans is True:
        ans = input_string("Add you smtp mail server. For example: smtp-mail.outlook.com","your.imapserver.com")
        config.set("smtp", "server", ans)
        ans = input_string("Add you smtp mail port", "25")
        config.set("smtp", "port", ans)
        ans = input_YN("Does your server use tls?", "Y")
        config.set("smtp", "tls", ans)
        ans = input_string("Add you smtp mail user", "your_user")
        config.cset("smtp", "user", ans)
        ans = input_string("Add you smtp mail password", "your_pass")
        config.cset("smtp", "password", ans)

    ans=input_YN("Do you want to change other server settings?")
    if ans is True:
        ans = input_string("How many concurrent database conections can be made by user for complex and long queries?","4")
        config.set("concurrency", "dbconnectionsbyuser", ans)
    config.save()
