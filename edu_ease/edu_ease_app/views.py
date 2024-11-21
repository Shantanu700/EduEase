from django.db import IntegrityError
from django.http import JsonResponse
import json
import re 
from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import *
from .utils import *

# Create your views here.
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            f_name = data.get('fname')
            if not f_name or not f_name.isalpha():
                return JsonResponse({"status":"Invalid First name"}, status=422)
            u_name = data.get('uname')
            if not u_name or not u_name.isalnum():
                return JsonResponse({"status":"Invalid User name"}, status=422)
            l_name = data.get('lname')
            if not l_name or not l_name.isalpha():
                return JsonResponse({"status":"Invalid Last name"}, status=422)
            e_mail = data.get('email')
            if not e_mail or not bool(re.match(r"[a-zA-Z0-9_\-\.]+[@][a-z]+[\.][a-z]{2,3}",e_mail)):
                return JsonResponse({"status":"Invalid Email"},status=422)
            passwd_1 = data.get('passwd')
            passwd_2 = data.get('cnf_passwd')
            if not (passwd_1 and passwd_2):
                return JsonResponse({"status":"Both passwords are required"},status=422)
            if passwd_1 != passwd_2:
                return JsonResponse({"status":"passwords do not match"}, status=409)
            if not bool(re.match(r"^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[0-9])(?=.*[a-z]).{8,16}$",passwd_1)):
                return JsonResponse({"status":"Weak Password, should include an upper case, a number, an special Symbol and should be of length between 8 to 16"},status=400)
            new_user = User.objects.create_user(u_name, e_mail, passwd_1)
            new_user.first_name = f_name
            new_user.last_name = l_name
            new_user.save()
            return JsonResponse({'status': 'success', 'f_name': f_name, 'u_name': u_name, 'l_name': l_name, },status=201)
        except IntegrityError:
            return JsonResponse({"status":"User already exists"}, status=409)
    return JsonResponse({"status":"Bad request"},status=400)

def signin(request):
    if request.method == 'GET':
        return JsonResponse({'is_authenticated':request.user.is_authenticated})

    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        username = data.get('uname')
        passwd = data.get('passwd')
        if username and passwd:
            if User.objects.filter(username=username).exists():
                user = authenticate(username=username,password=passwd)
                print(user)
                if user is not None:
                    login(request,user)
                    return JsonResponse({"status":"Logged in Successfully"},status=200 )
                return JsonResponse({"status":"Password entered is incorrect"},status=400)
            return JsonResponse({"status":"No user with these credentials"},status=400)
        return JsonResponse({'status':'Email and Password are required'},status=422)
    return JsonResponse({"status":"Invalid request method"},status=405)

def signout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({"status":"Logged out Successfully",'route':'/login'},status=200 )
        return JsonResponse({"status":"No User was autherized"},status=401)
    return JsonResponse({"status":"Invalid request method"},status=405)

def upload_document(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            doc_list = request.FILES.getlist('files')
            document_path_list = []
            if len(doc_list) > 3:
                return JsonResponse({'status':'You can\'t upload more than 3 pdfs at a time'}, status=422)
            for doc in  doc_list:
                document = Document(user=request.user,title=doc.name,file=doc)
                document.save()
                document_path_list.append(document.file.path)
            print(document_path_list)
            raw_text = get_pdf_text(document_path_list)
            text_chunks = get_text_chunks(raw_text)
            print(text_chunks)
            get_vector_store(text_chunks)
            return JsonResponse({'document_id': "saved"})
        return JsonResponse({"status":"Unautherized"},status=401)
    return JsonResponse({"status":"Invalid request method"},status=405)
        
def ask_question(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            question_text = data.get('question')
            print(question_text)
            ans =   user_input(question_text)
            print(ans)
            print(ans.get('output_text'))
            return JsonResponse({'answer': ans.get('output_text')})
        return JsonResponse({"status":"Unautherized"},status=401)
    return JsonResponse({"status":"Invalid request method"},status=405)

def get_fl_card(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            word = data.get('word')
            print(word)
            ans = user_input_word(word)
            print(ans)
            print(ans.get('output_text'))
            return JsonResponse({'answer': ans.get('output_text')})
        return JsonResponse({"status":"Unautherized"},status=401)
    return JsonResponse({"status":"Invalid request method"},status=405)
    