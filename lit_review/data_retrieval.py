'''
Created on Nov 8, 2012

@author: kpaskov
'''


@app.route("/reference")
@fresh_login_required
def reference():
#    try:
##        app.stop()
##        app.run()
#        refs = RefTemp.search()
#    except:
#        Database(DBUSER, DBPASS)
#        refs = RefTemp.search()
#    num_of_refs = len(refs.all())
#    return render_template('literature_review.html',
#                           ref_list=refs,
#                           ref_count=num_of_refs)
    return "reference()"
    

@app.route("/reference/delete/<pmid>")
@fresh_login_required
def discard_ref(pmid):

#    try:       
#        RefTemp.delete(pmid)
#        RefBad.insert(pmid, current_user.name.upper())
#        db.session.commit() #@UndefinedVariable
#    except:
#        db.session.rollback() #@UndefinedVariable
#        return "An error occurred when deleting the reference for pmid=" + pmid + " from the database."
#    return "Reference for pmid=" + pmid + " has been removed from the database!"
    return "discard_ref()"


@app.route("/reference/link/<pmid>/<parameters>")
@fresh_login_required
def link_ref(pmid, parameters):
    
#    reflink = ReferenceLink(pmid, current_user.name.upper(), parameters)
#    bad_names = reflink.invalid_names()
#    if len(bad_names) > 0:
#        return "Not found Gene name(s): " + ', '.join(bad_names)
#
#    err = 0
#                            
#    try:
#        message = reflink.insert_and_associate()
#        db.session.commit() #@UndefinedVariable
#    except:
#        db.session.rollback() #@UndefinedVariable
#        err = 1
#        raise
#
#    if err == 1:
#        return "An error occurred when linking the reference for pmid = " + pmid + " to the info you picked/entered: " + parameters
#    if message == None:
#        return "Reference for pmid = " + pmid + " has been added into the database."
#    return "Reference for pmid = " + pmid + " has been added into the database and associated with the following data:<p>" + message
    "return link_ref()"