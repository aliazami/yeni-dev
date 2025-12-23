class Project:
    def __init__(self):
        self.image_path = None
        self.annotations = []
        self.counter = 0

    def reset(self):
        self.image_path = None
        self.annotations.clear()
        self.counter = 0



class ProjectManager:
    def __init__(self):
        self.current = Project()

    def new_project(self):
        self.current = Project()