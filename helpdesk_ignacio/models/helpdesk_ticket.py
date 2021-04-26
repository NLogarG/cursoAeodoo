from odoo import models, fields, api

class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Action'

    name = fields.Char()
    date = fields.Date()
    ticket_id = fields.Many2one(
        comodel_name= 'helpdesk.ticket',
        string='Ticket')


class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Tag'

    name = fields.Char()
    ticket_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.tag',
        relation='helpdesk_ticket_tag_rel',
        column1='tag_id',
        column2='ticket_id',        
        string='Tags')

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket' 
    _description = 'Ticket'

    tag_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.tag',
        relation='helpdesk_ticket_tag_rel',
        column1='ticket_id',
        column2='tag_id',        
        string='Tags')

    action_ids = fields.One2many(
        comodel_name='helpdesk.ticket.action',
        inverse_name='ticket_id',
        string='Action')

    name = fields.Char(
        string="Name",
        required=True)
    description = fields.Text(
        string="Description",
        translate=True)
    date = fields.Date(
        string='Date')
    state = fields.Selection(
        [('nuevo','Nuevo'),
         ('asignado', 'Asignado'),
         ('proceso', 'En proceso'),
         ('pendiente', 'Pendiente'),
         ('resuelto', 'Resuelto'),
         ('cancelado', 'Cancelado')],
        string='State',
        default='nuevo')    
    time = fields.Float(
        string='Time')
    assigned = fields.Boolean(
        string='Assigned',
        compute='_compute_assigned')
    date_limit=fields.Date(
        string='Date Limit')
    action_corrective = fields.Html(
        string='Corrective Action',
        help='Descrive corrective actions to do')   
    action_preventive = fields.Html(
        string='Preventive Action',
        help='Descrive preventive actions to do')   
    
    
    def do_assign(self):
        self.ensure_one()
        self.write({
            'state': 'asignado',
            'assigned': True})    
    def proceso(self):
        self.ensure_one()
        self.state = 'proceso'    
    def pendiente(self):
        self.ensure_one()
        self.state = 'pendiente'
    def finalizar(self):
        self.ensure_one()
        self.state = 'resuelto'
    def cancelar(self):
        self.ensure_one()
        self.state = 'cancelado'

    user_id = fields.Many2one(
        comodel_name='res.users',
        srting='Asigned to')
    

    @api.depends('user_id')
    def _compute_assigned(self):
        for record in self:
            record.assigned = self.user_id and True or False
             
            
    
    #Crear campo calculado que indique, dentro de un ticket
    # la cantidad de tiquets asociados al mismo usuario.
    ticket_qty = fields.Integer(
        string='Ticket Qty',
        compute='_compute_ticket_qty')

    @api.depends('user_id')
    def _compute_ticket_qty(self):
        for record in self:
            other_tickets = self.env['helpdesk.ticket'].search([('user_id','=', record.user_id.id)])
            record.ticket_qty = len(other_tickets)

    # Creamos un campo nombre de etiqueta, y hacer un boton que cree la nueva etiqueta con ese nombre
    # y lo asocie al ticket.

    tag_name = fields.Char(
        string='Tag Name')

    def create_tag(self):
        self.ensure_one()
        self.write({
            'tag_ids': [(0,0, {'name': self.tag_name})]
        })
        