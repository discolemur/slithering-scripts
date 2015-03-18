" Remove bootstrap values
" %s/)\zs[0-9]*\ze//g
" Normalize all branch lengths
" %s/\.\zs[0-9]*\ze/05/g
"
"
"
"
" Remove branch lengths completely.
%s/\:[0-9]*\.[0-9]*//g
" Remove cluster IDs
%s/[(,]\zs[^(,]*\ze[OR]//g
" Simplify names and remove gene IDs
%s/OD.\{2\}\zs[^:]*\ze//g
%s/R_EP_0.\{2\}\zs[^:]*\ze//g
