from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from short_answer.forms import UserForm, UserProfileForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from short_answer.models import *

import driver2
import knn
import CosineDistance
import uuid


def index(request):
    print request.user.is_authenticated()
    if request.user.is_authenticated():
        if request.session['isStudent']==True:
            return HttpResponseRedirect('/short_answer/student_home')
        else:
            return HttpResponseRedirect('/short_answer/teacher_home')
    else:
        return render(request, 'short_answer/index.html')

def question_bank(request):

    if not request.user.is_authenticated():
        return render(request, 'short_answer/index.html')

    else:
        if request.session['isStudent'] == True:
            logout(request)
            return HttpResponseRedirect('/short_answer/')
        else:
            if request.method == 'POST':
                for i in range(0,100):
                    while True:
                        try:
                            selected_ques_list = request.POST.getlist('checkbox')
                            selected_ques = ','.join(selected_ques_list)
                            print selected_ques
                            testCode = uuid.uuid4().hex[:6].upper()
                            teacher_instance = User.objects.get(id = request.session['pkey'])
                            test_instance = Test.objects.create(test_code = testCode, question_nos = selected_ques, created_by = teacher_instance)
                            return HttpResponseRedirect('/short_answer/teacher_home/')
                        except IntegrityError as e:
                            continue
                        break
            else:
                all_questions = QuestionBank.objects.all()
                context = {'all_questions' : all_questions}
                return render(request, 'short_answer/QuestionBank.html', context)


def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'short_answer/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
          username = request.POST['username']
          password = request.POST['password']
          test_code = request.POST['tCode']
          role = request.POST.get('isStudent')

          if role == "Teacher":
              isStudent = False

          elif role == None:
              print  "invalid login details " + username + " " + password
              return render_to_response('short_answer/index.html', {}, context)
          else:
              isStudent = True

          user = authenticate(username=username, password=password)

          if user is not None:
              user2 = UserProfile.objects.get(user=user)
              #Student account
              if user2.isStudent and isStudent and user.is_active:
                  try:

                      test_code = request.POST['tCode']
                      test_instance = Test.objects.get(test_code = test_code)
                      login(request, user)
                      request.session['s_email'] = user.email
                      request.session['isStudent'] = user2.isStudent
                      request.session['pkey'] = user.id
                      request.session['test_code'] = test_code
                      return HttpResponseRedirect('/short_answer/student_home/')
                  except ObjectDoesNotExist as e:
                      return HttpResponse("INVALID TEST CODE!")

              elif user2.isStudent == False and isStudent:
                  return HttpResponse("INVALID LOGIN ATTEMPT!")
              elif user2.isStudent == True and isStudent == False:
                      return HttpResponse("INVALID LOGIN ATTEMPT!")

              # Teacher Account
              elif user2.isStudent == False and isStudent == False and user.is_active:
                  request.session['t_email'] = user.email
                  request.session['isStudent'] = user2.isStudent
                  request.session['pkey'] = user.id
                  login(request, user)
                  return HttpResponseRedirect('/short_answer/teacher_home/')


          else:
              # Return an 'invalid login' error message.
              print  "invalid login details " + username + " " + password
              return render_to_response('short_answer/index.html', {}, context)

    else:
        # the login is a  GET request, so just show the user the login form.
        return render_to_response('short_answer/index.html', {}, context)

def student_home(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/short_answer/')
    else:
        if request.session['isStudent'] == False:
            return HttpResponseRedirect('/short_answer/teacher_home')

        else:
            return render(request, 'short_answer/student_home.html')

def test_history(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/short_answer/')
    else:
        if request.session['isStudent'] == True:
            logout(request)
            return HttpResponseRedirect('/short_answer/')
        else:
            teacher_instance = User.objects.get(id = request.session['pkey'])
            tests = Test.objects.filter(created_by = teacher_instance)
            tests = list(tests)
            context = {'tests' : tests}
            return render(request, 'short_answer/test_history.html', context)

def test_detail(request, test_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/short_answer/')
    else:
        if request.session['isStudent'] == True:
            logout(request)
            return HttpResponseRedirect('/short_answer/')
        else:
            test_instance = Test.objects.get(id = test_id)
            ques_nos_string = test_instance.question_nos
            ques_nos_list = ques_nos_string.split(",")
            question_list = []
            for i in range (len(ques_nos_list)):
                question_list.append(QuestionBank.objects.get(id = ques_nos_list[i]))
            context = {'question_list' : question_list}
            return render(request, 'short_answer/test_detail.html', context)

def about(request):
    if not request.user.is_authenticated():
        context = {'home' : ''}
    else:
        if 't_email' in request.session:
            context = {'home' : 'teacher_home'}
        else:
            context = {'home' : 'student_home'}

    return render(request, 'short_answer/about.html', context)


def teacher_home(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/short_answer/')
    else:
        if request.session['isStudent'] == True:
            logout(request)
            return HttpResponseRedirect('/short_answer/')
        else:
            return render(request, 'short_answer/teacher_home.html')


def student_test(request):

    if not request.user.is_authenticated():
        return render(request, 'short_answer/index.html')
    else:
        if request.session['isStudent'] == False:
            return HttpResponseRedirect('/short_answer/teacher_home')
        else:
            test_code = request.session['test_code']
            test_instance = Test.objects.get(test_code = test_code)
            ques_nos_string = test_instance.question_nos
            ques_nos_list = ques_nos_string.split(",")
            question_list = []
            for i in range (len(ques_nos_list)):
                question_list.append(QuestionBank.objects.get(id = ques_nos_list[i]))
            context = {'question_list' : question_list}
            return render(request, 'short_answer/student_test.html', context)

def viewscore(request):
    stud_ans = request.POST.getlist('ans')
    reload_count = request.POST.get('reload_count')
    back_count = request.POST.get('back_count')
    tab_switch_count = request.POST.get('tab_switch_count')
    test_code = request.session['test_code']
    test_instance = Test.objects.get(test_code = test_code)
    ques_nos_string = test_instance.question_nos
    ques_nos_list = ques_nos_string.split(",")
    final_score_list = []
    scores = []
    for i in range (len(ques_nos_list)):
        train_file = QuestionBank.objects.get(id = ques_nos_list[i]).train_file
        student_answer = stud_ans[i]
        print student_answer
        print "Evaluating answer no. " + str(i)
        print "Training file used is " + str(train_file)
        scores.append(driver2.main(train_file, [student_answer]))


    print scores
    score1_LSA = scores[0]['lsa']
    score1_IG = scores[0]['ig']
    score2_LSA = scores[1]['lsa']
    score2_IG = scores[1]['ig']

    template = loader.get_template('short_answer/viewscore.html')
    context = {
'score1_LSA': str(score1_LSA[0]),
'score1_IG' : str(score1_IG[0]),
'score2_LSA' : str(score2_LSA[0]),
'score2_IG' : str(score2_IG[0])
}
    return HttpResponse(template.render(context, request))


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/short_answer/')
