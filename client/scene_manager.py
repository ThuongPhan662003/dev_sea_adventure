class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.active_scene = None

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def set_scene(self, name):
        if name in self.scenes:
            self.active_scene = self.scenes[name]
            self.active_scene.on_enter()

    def handle_event(self, event):
        if self.active_scene:
            self.active_scene.handle_event(event)

    def update(self):
        if self.active_scene:
            self.active_scene.update()

    def draw(self, screen):
        if self.active_scene:
            self.active_scene.draw(screen)
