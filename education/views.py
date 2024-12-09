from django.shortcuts import render, get_object_or_404, redirect
from .models import PatientEducationResource, Category
from .forms import PatientEducationResourceForm, ResourceSearchForm, CategoryForm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('resource_list')
    else:
        form = CategoryForm()
    return render(request, 'education/add_category.html', {'form': form})

def add_resource(request):
    if request.method == 'POST':
        form = PatientEducationResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.author = request.user  # Set the author as the logged-in user
            resource.save()
            return redirect('resource_list')  # Redirect to your list of resources
    else:
        form = PatientEducationResourceForm()

    # Retrieve all categories from the database
    categories = Category.objects.all()

    return render(request, 'education/add_resource.html', {'form': form, 'categories': categories})

def resource_list(request):
    # Get the search query from the GET request
    query = request.GET.get('query', '')

    resources = PatientEducationResource.objects.all()

    if query:
        # Perform search if a query is provided
        resources = search_resources(query)

    # Implement pagination: Show 10 resources per page
    paginator = Paginator(resources, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'education/resource_list.html', {
        'page_obj': page_obj,
        'query': query  # Pass the query back to the template to retain it in the search input
    })

def resource_detail(request, slug):
    resource = get_object_or_404(PatientEducationResource, slug=slug)
    related_resources = suggest_related_resources(resource.id)  # Call suggest_related_resources
    return render(request, 'education/resource_detail.html', {'resource': resource, 'related_resources': related_resources})

def suggest_related_resources(resource_id):
    # Get the content of the selected resource
    selected_resource = PatientEducationResource.objects.get(pk=resource_id)
    selected_content = selected_resource.content

    # Get the content of all resources excluding the viewed one
    other_resources = PatientEducationResource.objects.exclude(pk=resource_id)
    all_content = [resource.content for resource in other_resources]

    # Create a TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Fit and transform the content into TF-IDF features
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_content)

    # Transform the selected content into TF-IDF features
    selected_tfidf = tfidf_vectorizer.transform([selected_content])

    # Calculate cosine similarity between the selected content and all other content
    cosine_similarities = linear_kernel(selected_tfidf, tfidf_matrix).flatten()

    # Create a list of tuples (resource, similarity_score)
    related_resources = [(resource, cosine_similarities[i]) for i, resource in enumerate(other_resources)]

    # Sort the related resources by similarity score in descending order
    related_resources.sort(key=lambda x: x[1], reverse=True)

    return related_resources

def search_resources(query):
    # Get all resources
    resources = PatientEducationResource.objects.all()

    # Search in title and content fields
    search_texts = [resource.title + " " + resource.content for resource in resources]

    # Use TfidfVectorizer to process the search query and the resource content
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(search_texts)

    query_tfidf = tfidf_vectorizer.transform([query])
    cosine_similarities = linear_kernel(query_tfidf, tfidf_matrix).flatten()

    # Create a list of resources and their cosine similarity score
    resources_with_scores = [(resource, cosine_similarities[i]) for i, resource in enumerate(resources)]

    # Sort the resources by the similarity score in descending order
    resources_with_scores.sort(key=lambda x: x[1], reverse=True)

    # Return only the resources, sorted by relevance
    return [resource for resource, _ in resources_with_scores]


@login_required
def home_redirect(request):
    user_profile = request.user.userprofile  # Assuming a UserProfile model is linked
    if user_profile.usertype == 'doctor':
        return redirect('doctor_dashboard')  # Redirect to doctor dashboard
    elif user_profile.usertype == 'patient':
        return redirect('patient_dashboard')  # Redirect to patient dashboard
    elif user_profile.usertype == 'admin':
        return redirect('admin_dashboard')  # Redirect to admin dashboard
    else:
        return redirect('home') 