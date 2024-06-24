function warrantyValidate(){
      
    var name=document.formA.customer_name.value;
    var product=document.formA.product_id.value;
    
    if(name==null|| name.trim().length === 0 || name[0] === ' '){
        document.getElementById('namee').innerHTML="<i>Enter the Name</i>";
        document.formA.customer_name.focus();
        return false;
    }
    if(product==null||product==""){
        document.getElementById('pro').innerHTML="<i>Please select a product<i>";
        document.formA.product_id.focus();
        return false;
    }

    return true;
}

function productValidate(){
      
    var name=document.productForm.product_name.value;
    
    if(name==null|| name.trim().length === 0 || name[0] === ' '){
        document.getElementById('product_namee').innerHTML="<i>Enter the Product Name</i>";
        document.productForm.product_name.focus();
        return false;
    }

    return true;
}