"""Compositing Workflow；合同可由普通 Python 导入。"""
bl_info = {'name': 'Compositing Workflow', 'author': 'Blender AI', 'version': (0, 8, 0),
           'blender': (5, 2, 1), 'description': 'Managed compositor groups and guarded interactive relight preview',
           'category': 'Compositing'}


def register():
    from . import relight_preview_ui
    relight_preview_ui.register()


def unregister():
    from . import relight_preview_ui
    relight_preview_ui.unregister()
