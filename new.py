def user():
    Name = input("Enter the Name : ")
    Age = int(input("Enter the Age : "))
    Gender = input("Enter the Gender : ")
    return Name, Age, Gender

def profile(Name, Age, Gender):
    print("-" * 50)
    print("PROFILE CARD\n")
    print("Name : %s\t Age : %s" % (Name, Age))
    print("Gender : %s" % Gender)
    print("-" * 50)

Name, Age, Gender = user()
profile(Name, Age, Gender)
