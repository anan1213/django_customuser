from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views import generic
from .forms import LoginForm, UserCreateForm
from django.template.loader import get_template
from django.http import Http404, HttpResponseBadRequest
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Friends, Admit
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy

"""
get_user_model関数は、そのプロジェクトで使用しているUserモデルを取得します。デフォルトのUserか
、カスタムしたUserのどちらかです。どちらの場合でも動く汎用的なコードを書く場合には必須の記述で、
とりあえずUserモデルの取得にはこの関数を使いましょう。
"""
User = get_user_model()

class IndexView(generic.TemplateView):
    template_name = 'customuser/index.html'


class Login(LoginView):
    form_class = LoginForm
    template_name = 'customuser/login.html'

class Logout(LoginRequiredMixin, LogoutView):
    template_name = 'customuser/logout.html'



class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'customuser/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        #subject_template = get_template('customuser/mail_template/create/subject.txt')
        #subject = subject_template.render(context)

        subject = '本登録の続き'
        message_template = get_template('customuser/mail_template/create/message.txt')
        message = message_template.render(context)

        from_email = 'django.create.user@gmail.com'
        #user.email_user(subject, message, from_email)
        user.email_user(subject, message, from_email)
        return redirect('customuser:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'customuser/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'customuser/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class TestView(generic.TemplateView):
    template_name = 'customuser/test.html'

    def get_context_data(self, get_username, **kwargs):
        context = super().get_context_data(**kwargs)
        user_list = User.objects.filter(username = get_username)
        context = {
           'user_list': user_list
        }

        return context


"""
def get_current_user(request=None):
    if not request:
        return None
    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key).get_decoded()
    uid = session.get('id')

    return User.objects.get(id=uid)

"""

class ProfileDetailView(generic.DetailView):
    model = User
    template_name = 'customuser/profile.html'

    slug_field = 'username'
    slug_url_kwarg = 'get_name'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = get_object_or_404(User, username=self.kwargs['get_name'])
        context['user'] = User.objects.get(username=username)
        #context['user'] = get_current_user(self.request)
        context['following'] = Friends.objects.filter(follower__username=username).count()
        context['followers'] = Friends.objects.filter(following__username=username).count()


        #if username is not context['user'].username:
            #result = Connection.objects.filter(follower__username=context['user'].username).filter(following__username=username)
            #context['connected'] = True if result else False


        return context



@login_required
def follow_view(request, *args, **kwargs):
    try:
        follower = User.objects.get(username=request.user.username)
        following = User.objects.get(username=kwargs['get_name'])
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['get_name']))
        return HttpResponseRedirect(reverse_lazy('customuser:index'))


    if follower == following:
        messages.warning(request, '自分自身はフォローできません')
    else:
        admit = Admit(admit_follow=False)
        admit.save()
        _, created = Friends.objects.get_or_create(follower=follower, following=following, admit_follow=admit)


        if (created):
            messages.success(request, '{}をフォローしました'.format(following.username))
        else:
            messages.warning(request, 'あなたはすでに{}をフォローしています'.format(following.username))

    return HttpResponseRedirect(reverse_lazy('customuser:profile', kwargs={'get_name': follower.username}))



@login_required
def unfollow_view(request, *args, **kwargs):
    try:
        follower = User.objects.get(username=request.user.username)
        following = User.objects.get(username=kwargs['get_name'])
        if follower == following:
            messages.warning(request, '自分自身のフォローを外せません')
        else:
            unfollow = Friends.objects.get(follower=follower, following=following)
            unfollow.delete()
            messages.success(request, 'あなたは{}のフォローを外しました'.format(following.username))
    except User.DoesNotExist:
        messages.warning(request, '{}は存在しません'.format(kwargs['get_name']))
        return HttpResponseRedirect(reverse_lazy('customuser:index'))
    except Connection.DoesNotExist:
        messages.warning(request, 'あなたは{0}をフォローしませんでした'.format(following.username))

    return HttpResponseRedirect(reverse_lazy('customuser:profile', kwargs={'get_name': following.username}))



#class 
