from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name = "home"),
    path('room/<str:pk>', views.room, name = "room"),
    path('create_Room', views.createRoom, name = "createRoom"),
    path('update_Room/<str:pk>', views.updateRoom, name = "updateRoom"),
    path('delete_Room/<str:pk>', views.deleteRoom, name = "deleteRoom"),
    path('login_page',views.login_page, name= "login_page"),
    path('logout', views.logoutUser, name = "logoutUser"),
    path('register', views.reg, name = "reg"),
    path('deleteMsg/<str:pk>', views.deleteMsg,name = "deleteMsg"),
    path('userProfile/<str:pk>', views.userProfile, name = "userProfile"),
    path('edituser/', views.editUser,name = "editUser"),
    path('mobtop/', views.mobtop, name = "mobtop"),
    path('mobact/<str:pk>', views.mobact, name = "mobact")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)