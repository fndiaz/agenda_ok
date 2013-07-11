# coding=UTF-8
import datetime, os, commands

def principal():
	response.title="principal"
	if session.aut == '0':
		funcao = request.vars['f']
		redirect(URL("redireciona", "/%s" %(funcao)))
	
	agen_glo = db.executesql("SELECT empresa, telefone from agenda WHERE particular = 'F' order by id desc LIMIT 4;")
	agen_par = db.executesql("SELECT empresa, telefone from agenda WHERE particular = 'T' and ramal = %s order by id desc LIMIT 4;" %str(session.ramal))
	ligacoes = db.executesql("SELECT * from agenda_lg WHERE ramal = %s order by id desc LIMIT 8;" %str(session.ramal))
	#print ligacoes

	return response.render("initial/principal.html", agen_glo=agen_glo, agen_par=agen_par, ligacoes=ligacoes)

def agenda():
	response.title="Global"
	if session.aut == '0':
		funcao = request.vars['f']
		redirect(URL("redireciona", "/%s" %(funcao)))

	query = (db.agenda.particular == 'F')
	#print query
	db.agenda.id.readable=False
	db.agenda.particular.readable=False
	db.agenda.ramal.readable=False
	fields = (db.agenda.id, db.agenda.empresa, db.agenda.telefone, 
				db.agenda.contato, db.agenda.dep, db.agenda.particular, db.agenda.ramal)
	

	print session.permissao			
	if session.permissao == 0:
		print "agenda sem permissao"
		deleta=False
		links=[lambda row: A('Discar', 
   			      _class='btn', 
   			      _title='Discar', 
   		    	  _href=URL("initial", "/ligacao", 
   		      	vars=dict(n=row.telefone, e=row.empresa, f='agenda')))]
		
   	else:
   		print "agenda com permissao"
   		deleta=True	
		links=[lambda row: A('Discar', 
   			      _class='btn', 
   			      _title='Discar', 
   		    	  _href=URL("initial", "/ligacao", 
   		      	vars=dict(n=row.telefone, e=row.empresa, f='agenda'))),
				lambda row: A('Editar', 
   		      	_class='btn', 
   		      	_title='Editar', 
   		      	_href=URL("initial", "/edit", 
   		      	vars=dict(f=row.id)))]	

	grid = SQLFORM.grid(query=query, fields=fields, csv=False,
					details=False, searchable=True, deletable=deleta, editable=False, 
					create=False, links=links, user_signature=False, orderby=db.agenda.empresa)

	return response.render("initial/show_grid.html", grid=grid)


def agenda_particular():
	response.title="Particular"
	if session.aut == '0':
		funcao = request.vars['f']
		redirect(URL("redireciona", "/%s" %(funcao)))
	
	print 'agenda particular'
	query = ((db.agenda.ramal == session.ramal) & (db.agenda.particular == 'V'))
	#print query

	db.agenda.id.readable=False
	db.agenda.particular.readable=False
	db.agenda.ramal.readable=False
	fields = (db.agenda.id, db.agenda.empresa, db.agenda.telefone, 
				db.agenda.contato, db.agenda.dep, db.agenda.particular, db.agenda.ramal)
	#headers = {'hosts.id':   'ID',
	#           'hosts.servicos': 'Servicos'}
	links=[lambda row: A('Discar', 
   			      _class='btn', 
   			      _title='Discar', 
   		    	  _href=URL("initial", "/ligacao", 
   		      	vars=dict(n=row.telefone, e=row.empresa, f='agenda_particular'))),
				lambda row: A('Editar', 
   		      	_class='btn', 
   		      	_title='Editar', 
   		      	_href=URL("initial", "/edit", 
   		      	vars=dict(f=row.id)))] 
   
	grid = SQLFORM.grid(query=query, fields=fields, csv=False,
					details=False, searchable=True, deletable=True, editable=False, 
					create=False, links=links, user_signature=False, orderby=db.agenda.empresa)

	return response.render("initial/show_grid.html", grid=grid)


def ligacao():
	telefone = request.vars['n']
	empresa = request.vars['e']
	ramal = str(session.ramal)
	ramal_fis = str(session.ramal_fis)
	tecnologia = str(session.tecnologia)
	funcao = request.vars['f']
	if funcao == 'agenda':
		particular = 'F'
	if funcao == 'agenda_particular':
		particular = 'T'

	f = open('/tmp/000.cal','w')
	f.write('Channel: %s/%s\n' %(tecnologia, ramal_fis))
	f = open('/tmp/000.cal','a')
	f.write('Context: ramais\n')
	f = open('/tmp/000.cal','a')
	f.write('Extension: %s\n' %(telefone))
	f = open('/tmp/000.cal','a')
	f.write('Callerid: agenda\nMaxRetries: 1\nRetryTime: 30\nWaitTime: 60')
	f.close()
	commands.getoutput("chmod 777 /tmp/000.cal")
	commands.getoutput("cp /tmp/000.cal /var/spool/asterisk/outgoing/")

	now = str(datetime.datetime.now())
	now=now.split('.')[0]
	teste = db.executesql("INSERT INTO agenda_lg (ramal, telefone, empresa, datetime, particular) VALUES('%s', '%s', '%s', '%s', '%s');" %(ramal, telefone, empresa, now, particular))
	print teste
	print 'Ligação do ramal %s para número %s' %(str(session.ramal), telefone)

	session.flash = "Ligação do ramal %s para número %s" %(str(session.ramal), telefone)
	redirect(URL("initial", "/%s" %(funcao)))


def redireciona():
	if session.aut != '0':
		funcao = request.vars['f']
		redirect(URL("initial", "/%s" %(funcao)))
		#redirect(URL("initial", "/permissao?f=%s" %(funcao)))
	else:
		print 'ramal %s nao esta logado (redireciona)' %(session.aut)
		session.flash = "Faça o login"
		redirect(URL("initial", "/log_in"))

def permissao():
	#permissao add
	if session.permissao == 0:
		redirect(URL("initial", "/addition2"))
	else:
		redirect(URL("initial", "/addition"))


def addition():

    form = SQLFORM(db.agenda, submit_button='Adicionar', 
    		fields = ['empresa', 'telefone', 'contato', 'dep', 'particular', 'ramal'], 
			labels = {'empresa':'Empresa', 'telefone':'Telefone', 
						'contato':'Contato', 'dep':'Departamento', 
						'particular':'Particular', 'ramal':'Ramal'},)
    form.vars.ramal = session.ramal

    response.title="Contato"
    if session.permissao == 0:
		redirect(URL("initial", "/addition2"))
    if session.aut == '0':
		funcao = request.vars['f']
		redirect(URL("redireciona", "/%s" %(funcao)))


    if form.process().accepted:
    	#evento = request.vars
    	#confno = form.vars.id
    	#email(evento, confno)
    	response.flash = 'Inserido com sucesso'
    	print form.vars.particular
    	if form.vars.particular == True:
    		redirect(URL("initial", "/agenda_particular"))
    	else:
    		redirect(URL("initial", "/agenda"))			
    elif form.errors:
    	response.flash = 'Ops, algo não está correto'
    else:
    	response.flash = 'Insira os dados do formulário'
    return response.render("initial/show_form2.html", form=form)

def addition2():
	
    form = SQLFORM(db.agenda, submit_button='Adicionar', 
    		fields = ['empresa', 'telefone', 'contato', 'dep', 'ramal'], 
			labels = {'empresa':'Empresa', 'telefone':'Telefone', 
						'contato':'Contato', 'dep':'Departamento', 
						'ramal':'Ramal'},)
    form.vars.ramal = session.ramal
    form.vars.particular = True

    response.title="Contato"
    if session.aut == '0':
		funcao = request.vars['f']
		redirect(URL("redireciona", "/%s" %(funcao)))

    if form.process().accepted:
    	#evento = request.vars
    	#confno = form.vars.id
    	#email(evento, confno)
    	response.flash = 'Inserido com sucesso'
    	print form.vars.particular
    	if form.vars.particular == True:
    		redirect(URL("initial", "/agenda_particular"))
    	else:
    		redirect(URL("initial", "/agenda"))			
    elif form.errors:
    	response.flash = 'Ops, algo não está correto'
    else:
    	response.flash = 'Insira os dados do formulário'
    return response.render("initial/show_form2.html", form=form)


def edit():
    form = SQLFORM(db.agenda, request.vars['f'], submit_button='Editar')

    if form.process().accepted:
       response.flash = 'Editado com sucesso'
    elif form.errors:
       response.flash = 'Ops, algo não está correto'
    else:
       response.flash = 'Edite os dados do formulário'

    return response.render("initial/show_form2.html", form=form)


def log_in():
	#adicionar
    form = SQLFORM.factory(
    		Field("ramal", requires = IS_NOT_EMPTY(error_message=
						T("valor não pode ser nulo"))),
    		Field("senha", "password"),
    		formstyle="divs",
    		)

    response.title="login"
    if form.process().accepted:
    	ramal_dig = form.vars.ramal
    	senha_dig = form.vars.senha
    	print 'ramal digitado:%s  senha digitada:%s' %(ramal_dig, senha_dig) 
    	teste = db.executesql("SELECT v.ramal_virtual, v.nome, f.username, p.agenda_senha, f.tecnologia, p.agenda_nivel FROM ramal_virtual v LEFT JOIN ramal f ON v.username_ramalfisico = f.username INNER JOIN permissao p ON v.id_ramalvirtual = p.id_ramalvirtual WHERE v.ramal_virtual = %s;" %(ramal_dig))
    	print 'busca sql: %s' %str(teste)

    	if teste == ():
    		print "ramal incorreto"
    		response.flash = 'Ramal incorreto'
    	else:
    		usuario=teste[0][1]
    		senha=teste[0][3]

    		print 'usuario senha'
    		print session.ramal, usuario, session.ramal_fis, senha
    	   	#if ramal_dig == ramal:
    		#	print "ramal ok"
    		if senha_dig == senha:
    			print "senha ok"
    			session.ramal=teste[0][0]
    			session.ramal_fis=teste[0][2]
    			session.tecnologia=teste[0][4]
    			session.permissao=teste[0][5]
    			print 'permissao %s' %(session.permissao)
    			session.aut=session.ramal

    			print'login efetuado %s (log_in)' %(session.ramal)
    			session.flash = 'Bem Vindo %s' %(usuario)
    			redirect(URL("initial", "/principal"))
    		else:
    			print 'senha incorreta'
    			response.flash = 'Senha incorreta'	
    return response.render("initial/show_form.html", form=form)


def log_out():
	session.aut='0'
	session.ramal='0'
	session.ramal_fis='0'
	session.tecnologia='0'
	print session.aut
	print "logout (log_out)"
	redirect(URL("initial", "/log_in"))














def email(evento, confno):

	membros = evento.membros_user
    	for a in membros:        
   			print 'membro:',a
   			teste = db.executesql('SELECT nome, email, pin FROM usuario WHERE id = %s;' %str(a))
   			print  'select:',teste[0][0], teste[0][1], teste[0][2]
   			nome = teste[0][0] #está dando problema no envio
   			email = str(teste[0][1])
   			pin = str(teste[0][2])
   			print type(email)
   			print evento.starttime, evento.endtime, confno
   			mail.send(
			to="fndiaz02@gmail.com",#variavel email
			subject="Conferência",
			message="<html>A conferência %s acaba de ser criada e você é um membro, seguem os dados:<br>Horário de Início: %s<br>Horário de Término: %s<br>Pin: %s%s</html>" % (nome, confno, evento.starttime, evento.endtime, confno, pin)
			)

   	admin = evento.admin_user
   	for a in admin:
   		print 'admin:',a
   		teste = db.executesql('SELECT nome, email FROM usuario WHERE id = %s;' %str(a))
   		print 'select:',teste[0][0], teste[0][1]
   		print evento.starttime, evento.endtime, confno

def user():
	#if request.args(0) == 'register':
    #    	db.auth_user.bio.writable = db.auth_user.bio.readable = False
	return response.render("initial/user.html", user=auth())

def register():
	return auth.register()

def login():
        return auth.login()

def account():
    return dict(register=auth.register(),
                login=auth.login())
	
def download():
	return response.download(request, db)



	



