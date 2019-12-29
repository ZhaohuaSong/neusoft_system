__version__ = '1.0.4'
__all__ = (
    'View', 'GenericView', 'GenericModelView',
    'RedirectView', 'TemplateView', 'FormView',
    'ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView', 'QUpdateView'
)

from django.views.generic import View
from ..vanilla.views import (
    GenericView, RedirectView, TemplateView, FormView
)
from ..vanilla.model_views import (
    GenericModelView, ListView, DetailView, CreateView, UpdateView, DeleteView,QUpdateView
)
