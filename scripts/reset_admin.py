from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
password = 'password1234'
email = 'admin@example.com'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Stats: Updated existing user '{username}'. Password reset to '{password}'.")
except User.DoesNotExist:
    User.objects.create_superuser(username, email, password)
    print(f"Stats: Created new superuser '{username}'. Password set to '{password}'.")
