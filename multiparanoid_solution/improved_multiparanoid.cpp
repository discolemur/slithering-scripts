#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// This structure is the one that we'll use for all of our work
// Initially aclid will be -1 for every row.  gclid and gsid come directly from
// the input file.  The algorithm for merging clusters is:
//
//  Start assigning aclid values with 0
//  Start at the top of the array of rows
//      Assign the row the next aclid value (then increment the next aclid)
//      Work forward - as long as the gclid value doesn't change, assign the next row the same aclid
//      When the gclid does change, then start looking through the array for other instance that share this row's gsid.
//      When you do find one, assign all rows with that gclid to have this aclid
//      Keep doing that until you reach the end of the array
//      Now move to the next row.  If it doesn't have an aclid, then assign it (and all following with the same gclid)
//      If it does have an aclid, then just do the search for any future rows that have the same gclid
//      When you run out of rows, you're done.
struct row
{
    long aclid;         // aggregate cluster ID
    long gclid;         // global cluster ID
    long gsid;          // global sequence ID
};

long file_numrows(const char * fname)
{
    long rows = 0;
    char readbuf[2048];
    
    FILE *ifp = fopen(fname, "r");
    if(ifp)
    {
        while(fgets(readbuf, sizeof(readbuf), ifp))
        {
            if(*readbuf != '#' && *readbuf != '\n')
                rows++;
        }
    }
    fclose(ifp);
    return rows;
}

long file_to_rows(const char *fname, row *rows, long nrows)
{
    long nRows = 0;
    char readbuf[2048];
    row *pRow = rows;
    
    FILE *ifp = fopen(fname, "r");
    if(ifp)
    {
        while(fgets(readbuf, sizeof(readbuf), ifp))
        {
            if(*readbuf != '#' && *readbuf != '\n')
            {
//                printf(readbuf);
                pRow->aclid = -1;
                pRow->gclid = atol(readbuf);
                
                char *ptr = strchr(readbuf, '\t');
                if(!ptr)
                {
                    printf("No second column???  This is harmful or fatal.  Row %ld\n", nRows);
                    break;  // This should cause the process to fall down.
                }
                pRow->gsid = atol(++ptr);
                
                nRows++;
                pRow++;
            }
        }
    }
    fclose(ifp);
    
    return nRows;
}

bool assign_aclid(long rownum, row *rows, long nrows)
{
    bool rv = false;
    static long aclid = 1;
    
    // If this row doesn't already have an aclid, then assign the next aclid to this row
    if(rows[rownum].aclid < 0)
        rows[rownum].aclid = aclid++;

    // And assign the same aclid to all future rows that have the same gclid.
    // Note that we only have to look until the gclid changes, because the input file is sorted by gclid.
    long assigned_aclid = rows[rownum].aclid;
    long this_gclid = rows[rownum].gclid;
    for(long n = rownum + 1; rownum < nrows && rows[n].gclid == this_gclid; n++)
        rows[n].aclid = assigned_aclid;
        
    return rv;
}

void assimilate_aclid(long aclid_to_assimilate, long new_aclid, row *rows, long nrows)
{
    for(long n = 0; n < nrows; n++)
    {
        if(rows[n].aclid == aclid_to_assimilate)
            rows[n].aclid = new_aclid;
    }
}

void assign_cluster_to_aclid(long aclid, long rownum, row *rows, long nrows)
{
    long this_gclid = rows[rownum].gclid;
    long n = rownum;
    
    if(rows[rownum].aclid == aclid)
        return;
    
    if(rows[rownum].aclid != -1)
    {
        assimilate_aclid(rows[rownum].aclid, aclid, rows, nrows);
    }
    else
    {
        while(n > 0 && rows[n].gclid == this_gclid)
            n--;
    
        if(rows[n].gclid != this_gclid)
            n++;

        while(n < nrows && rows[n].gclid == this_gclid)
            rows[n++].aclid = aclid;
    }
}

// Use the aclid that was assigned to row[n]
// Look at all rows below n.
// If they have the same gsid as row[n], then
//  go back to the start of that series of rows having that gclid
//  and assign all of them to have this aclid.
void find_matches(long rownum, row *rows, long nrows)
{
    long this_aclid = rows[rownum].aclid;
    long this_gsid = rows[rownum].gsid;
    
    for(long n = rownum + 1; n < nrows; n++)
    {
        if(rows[n].gsid == this_gsid)
            assign_cluster_to_aclid(this_aclid, n, rows, nrows);
    }
}

void do_merge(row *rows, long nrows)
{
    long n = 0;
    
    for(n = 0; n < nrows; n++)
    {
        if(!(n % 5000) || n == nrows - 1)
            printf("%ld%% complete\n", n * 100 / (nrows - 1));
            
        assign_aclid(n, rows, nrows);
        find_matches(n, rows, nrows);
    }
}

void print_rows(row *rows, long nrows, const char* ofname)
{
    FILE *ofp = fopen(ofname, "w");
    if(ofp)
    {
        for(long n = 0; n < nrows; n++)
            fprintf(ofp, "%ld\t%ld\t%ld\n", rows[n].aclid, rows[n].gclid, rows[n].gsid);
    }
    fclose(ofp);
}

int main(int argc, const char * argv[])
{
    if (argc != 3) {
        printf("\nUsage: %s <combined.disco (input)> <merged.disco (output)>\n\n", argv[0]);
	printf("I require files as arguments, but commonly they are called combined.disco and merged.disco.\n");
        return 1;
    }
    // argv[1] is the input filename
    // argv[2] is the output filename
    long nlines = file_numrows(argv[1]);
    printf("Number of rows: %ld\n", nlines);
    
    row *rows = (row *)malloc(nlines * sizeof(row));
    
    if(file_to_rows(argv[1], rows, nlines) == nlines)
    {
        do_merge(rows, nlines);
    }
    
    print_rows(rows, nlines, argv[2]);
    
    free(rows);
    return 0;
}

