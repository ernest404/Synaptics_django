from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime
from .models import TriggerWord
from .utils.analyze import highlighter, wordcloudgen
from .utils.extract import article_extractor
from .utils.lex_rank import LexRankSummarizer
from .utils.todocx import doc_builder

# Create your views here.
def index(request):
    context = {
        'current_year': datetime.now().year,
    }
    return render(request, "index.html", context)

def analyze(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('pdf_file')  #make sure it matches with the form input name
        triggerwords = [tw.word for tw in TriggerWord.objects.all()]
        # try:
        highlighted_pdf_bytes = highlighter(uploaded_file, triggerwords)
        wordcloud_url = wordcloudgen(uploaded_file)
        context = {
        'current_year': datetime.now().year,
        'highlighted_newspaper': highlighted_pdf_bytes,
        'wordcloud_url':wordcloud_url}
        return HttpResponseRedirect(reverse("analyze"), context)
        
        # except Exception as e:
        #     context = {
        #     'current_year': datetime.now().year,
        #     'error_message': "Something is wrong with your file"}
        #     return render(request, "analyze.html", context)
    
    else:
        context = {
            'current_year': datetime.now().year,
        }
        return render(request, "analyze.html", context)
    
    
def summarize(request):
    context = {'current_year': datetime.now().year}

    if request.method == 'POST':
        uploaded_file = request.FILES.get('pdf_file')
        triggerwords = [tw.word for tw in TriggerWord.objects.all()]

        try:
            articles = article_extractor(uploaded_file)
            n_sentences = 4  # Example: Request number of sentences to summarize to

            # Invoke lexical summarizer
            lr = LexRankSummarizer(n_sentences)

            
            summary_list = []
            for article in articles:
                summary_list.append(lr(article))

            # Remove any duplicates from the list
            summary_list = list(dict.fromkeys(summary_list))
            request.session['summary_list'] = summary_list

            # Update context with additional data
            context.update({
                'filename': uploaded_file.name,
                'summary_list': summary_list,
            })

        except Exception as e:
            context['error_message'] = "Something is wrong with your file"

    # Note: You use the same template for both POST and GET requests here
    return render(request, "summarize.html", context)
    
def download_report(request):
    # Retrieve summary_list from session
    summary_list = request.session.get('summary_list', [])

    # Proceed only if there's a summary_list
    if summary_list:
        # Generate document
        document_stream = doc_builder(summary_list)

        # Set up HttpResponse
        response = HttpResponse(document_stream.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="summary_report_{}.docx"'.format(datetime.now().strftime("%Y%m%d"))

        # Optionally, clear the summary_list from session after downloading
        del request.session['summary_list']

        return response
    else:
        # Handle the case where summary_list is not available
        return HttpResponse("No summary available to download.", status=404)
