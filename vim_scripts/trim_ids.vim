" Remove cluster IDs
%s/[(,]\zs[^(,]*\ze[OR]//g
" Simplify names and remove gene IDs
%s/OD.\{2\}\zs[^:]*\ze//g
%s/R_EP_0.\{2\}\zs[^:]*\ze//g
