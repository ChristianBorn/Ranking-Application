function confirmation(link){
    if (confirm("Are you sure you want to delete this?")){
        open(link, "_self");
    }
}