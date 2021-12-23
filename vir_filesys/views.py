from django.shortcuts import render
from django.http import HttpResponse
import os
from django.views.generic import TemplateView
from django.shortcuts import render
from django.shortcuts import redirect


# Create your views here.
def home_view(request):
    file_path = '/'
    files = os.listdir(file_path)
    files = sorted(files)
    files = [file for file in files if not file.startswith('.')]
    # accepted_formats = ['jpg', 'img', 'png', 'jpeg']
    page_header = 'These are the contents of the root directory\n'
    for file in files:
        print(os.path.abspath(file))
        # if file.split('.')[-1] in accepted_formats:
        # response += "<p><a href='/open/" + file + "'>" + file + "</a></p>"
    # return HttpResponse(response)
    context = {'files': files,
               "current_dir": file_path,
               "page_header": page_header}
    return render(request, template_name='vir_filesys/home_view.html', context=context)


class OpenView(TemplateView):
    template_name = 'vir_filesys/open_file.html'
    home_template = 'vir_filesys/home_view.html'
    # dir_path = '/home/harshad/Downloads/'
    accepted_image_formats = ('jpg', 'img', 'png', 'jpeg')
    accepted_pdf_formats = ('pdf',)
    accepted_video_formats = ('mp4', 'webm', 'mkv')

    def dispatch(self, request, *args, **kwargs):
        method = self.request.POST.get('_method', '').lower()
        if method and method == "delete":
            return self.delete(*args, **kwargs)
        return super(OpenView, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        if request.session.get('previous_dir'):
            previous_dir = request.session['previous_dir']
            files = os.listdir(previous_dir)
            files = sorted(files)
            files = [file for file in files if not file.startswith('.')]
            context = {"files": files,
                       "current_dir": previous_dir}
            return render(request, template_name=self.home_template, context=context)
        else:
            return redirect(home_view)

    def post(self, request, **kwargs):
        previous_dir = request.POST.get("current_dir")
        current_dir = previous_dir + request.POST.get('directory')
        request.session['previous_dir'] = previous_dir
        request.session['current_dir'] = current_dir
        if os.path.isdir(current_dir):
            files = os.listdir(current_dir)
            files = sorted(files)
            files = [file for file in files if not file.startswith('.')]
            context = {"files": files,
                       "current_dir": current_dir + '/'}
            return render(request, template_name=self.home_template, context=context)
        elif os.path.isfile(current_dir):
            requested_file = request.POST.get('directory')

            # Render images
            if requested_file.endswith(self.accepted_image_formats):
                context = {"filename": requested_file,
                           "dir": 'images/' + requested_file,
                           "previous_dir": previous_dir,
                           "current_dir": current_dir,
                           "file_type": "image"}
                return render(request, template_name=self.template_name, context=context)

            # Render pdf files
            if requested_file.endswith(self.accepted_pdf_formats):
                context = {"filename": requested_file,
                           "dir": 'pdf/' + requested_file,
                           "previous_dir": previous_dir,
                           "current_dir": current_dir,
                           "file_type": "pdf"}
                return render(request, template_name=self.template_name, context=context)

            # Render videos
            if requested_file.endswith(self.accepted_video_formats):
                context = {"filename": requested_file,
                           "dir": 'videos/' + requested_file,
                           "previous_dir": previous_dir,
                           "current_dir": current_dir,
                           "file_type": "video"}
                return render(request, template_name=self.template_name, context=context)

        else:
            response = "Not a dir. The only dirs in this location are:\n"
            subdirs = [f.path for f in os.scandir(previous_dir) if f.is_dir()]
            for f in subdirs:
                response += '<p>' + f + '</p>'
            return HttpResponse(response)

    def delete(self, *args, **kwargs):
        current_dir = self.request.POST.get('current_dir')
        file_to_delete = current_dir + self.request.POST.get('file_name')

        if file_to_delete:
            try:
                os.remove(file_to_delete)
            except Exception as e:
                print("Couldn't delete the file. Try again.")
        return redirect("open_view")

