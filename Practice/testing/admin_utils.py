from nested_inline.admin import NestedModelAdmin

class CustomNestedModelAdmin(NestedModelAdmin):
    def add_nested_inline_formsets(self, request, inline, formset, depth=0):
        if depth > 5:
            raise Exception("Maximum nesting depth reached (5)")
        for form in formset.forms:
            nested_formsets = []
            for nested_inline in inline.get_inline_instances(request):
                InlineFormSet = nested_inline.get_formset(request, form.instance)
                prefix = "%s-%s" % (form.prefix, InlineFormSet.get_default_prefix())

                if request.method == 'POST' and any(s.startswith(prefix) for s in request.POST.keys()):
                    nested_formset = InlineFormSet(request.POST, request.FILES,
                                                   instance=form.instance,
                                                   prefix=prefix, queryset=nested_inline.get_queryset(request), request = request)   #TODO
                else:
                    nested_formset = InlineFormSet(instance=form.instance,
                                                   prefix=prefix, queryset=nested_inline.get_queryset(request))    #TODO
                nested_formsets.append(nested_formset)
                if nested_inline.inlines:
                    self.add_nested_inline_formsets(request, nested_inline, nested_formset, depth=depth + 1)
            form.nested_formsets = nested_formsets
