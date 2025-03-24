class PrintManager:
    def __init__(self):
        # Print settings
        self.show_debug = False
        self.show_status = True
        self.show_datacubby = False  # Add this line
        self.show_variable_testing = False  # For tracking variable creation and processing
        self.show_variable_basic = False   # For basic variable creation and operation status
       
    def debug(self, message):
        """For detailed debugging information"""
        # print("self.show_debug: ", self.show_debug)
        if self.show_debug:
            print(message)
            
    def status(self, message):
        """For important status updates"""
        # print("self.show_status: ", self.show_status)
        if self.show_status:
            print(message)
            
    def datacubby(self, message):
        """For data cubby specific messages"""
        # print("self.show_datacubby: ", self.show_datacubby)
        if self.show_datacubby:  # Simplified since we know attribute exists
            print(message)
            
    def variable_testing(self, message):
        """For tracking variable creation and handling operations"""
        if self.show_variable_testing:
            print(f"[VAR] {message}")
            
    def variable_basic(self, message):
        """For basic variable creation and operation status (can be toggled separately)"""
        if self.show_variable_basic:
            print(f"[VAR] {message}")

# Create global instance
print_manager = PrintManager()
print('initialized print_manager')
