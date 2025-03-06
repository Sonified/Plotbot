import requests
from getpass import getpass
from .print_manager import print_manager

class ServerAccess:
    def __init__(self):
        self._username = None
        self._password = None
        self._session = None
        self._password_type = None
        self.password_prompts = {
            'mag': "🧲 Enter your PASSWORD for restricted PSP FIELDS data: ",
            'sweap': "⚛️⚡️ Enter your PASSWORD for restricted PSP SWEAP data: "
        }
        print_manager.debug("🔐 ServerAccess initialized")
    
    @property
    def password_type(self):
        return self._password_type
        
    @password_type.setter
    def password_type(self, value):
        if value != self._password_type:  # If password type changes
            self._password = None  # Clear the password
        self._password_type = value
    
    @property
    def username(self):
        print_manager.debug(f"🔑 Current username: {self._username}")
        if self._username is None:
            self._username = getpass("🔒 Non-Public Data Request. 🙋🏿‍♂️ Enter your USER NAME for PSP Data Access")
        return self._username
    
    @username.setter
    def username(self, value):
        print_manager.debug(f"✍️ Setting username to: {value}")
        self._username = value
    
    @property
    def password(self):
        if self._password is None:
            prompt = self.password_prompts.get(self._password_type, "Enter your PSP data server password: ")
            self._password = getpass(prompt)
        return self._password
    
    @password.setter
    def password(self, value):
        self._password = value
    
    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
        return self._session
    
    def clear(self):
        """Clear stored credentials on failed auth."""
        self._password = None
        self._username = None

# Create global instance
server_access = ServerAccess()
print('initialized server_access') 