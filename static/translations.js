// Sistema de traducciones dinámicas para Gastos App
// Incluye todos los 341 textos encontrados

const translations = {
    es: {
        // === TÍTULOS Y HEADERS ===
        pageTitle: "💳 Gestión de Gastos",
        headerTitle: "Gestión de Gastos",
        sidebarUserRole: "Usuario",
        sidebarAdminRole: "Administrador",
        sidebarPrincipal: "Principal",
        sidebarGestion: "Gestión",
        sidebarLogout: "Cerrar Sesión",
        
        // === DESCRIPCIONES PRINCIPALES ===
        mainDescription: "Añade y gestiona tus gastos",
        addTicketDescription: "Añade un gasto individual con foto y extracción automática",
        multipleTicketsDescription: "Procesa varios tickets a la vez con verificación inteligente",
        manageGroupsDescription: "Organiza y administra tus grupos de gastos",
        groupsManagementDescription: "Organiza tus gastos en grupos personalizados",
        selectDateRange: "Selecciona el rango de fechas para filtrar tus gastos",
        dashboardDescription: "Visualiza y confirma tus gastos",
        dashboardDateFilterDescription: "Selecciona el rango de fechas para el dashboard",
        
        // === FORMULARIOS Y CAMPOS ===
        date: "Fecha",
        concept: "Concepto",
        reason: "Motivo",
        description: "Descripción",
        amount: "Importe",
        currency: "Moneda",
        image: "Imagen",
        user: "Usuario",
        trip: "Viaje",
        
        // === BOTONES PRINCIPALES ===
        addExpense: "Añadir Gasto",
        addTrip: "Añadir Viaje",
        addTripDetail: "Añadir Detalle",
        exportData: "Exportar Datos",
        settings: "Configuración",
        save: "Guardar",
        cancel: "Cancelar",
        edit: "Editar",
        delete: "Eliminar",
        close: "Cerrar",
        confirm: "Confirmar",
        clear: "Limpiar",
        
        // === CONCEPTOS ===
        restaurant: "Restaurante",
        transport: "Transporte",
        accommodation: "Alojamiento",
        fuel: "Combustible",
        shopping: "Compras",
        entertainment: "Entretenimiento",
        health: "Salud",
        education: "Educación",
        technology: "Tecnología",
        others: "Otros",
        
        // === ESTADOS Y VALORES ===
        checked: "Revisado",
        unchecked: "Sin revisar",
        squared: "Cuadrado",
        notSquared: "Sin cuadrar",
        active: "Activo",
        inactive: "Inactivo",
        yes: "Sí",
        no: "No",
        all: "Todos",
        
        // === MENSAJES DEL SISTEMA ===
        success: "Éxito",
        error: "Error",
        warning: "Advertencia",
        info: "Información",
        loading: "Cargando...",
        saving: "Guardando...",
        deleting: "Eliminando...",
        processing: "Procesando",
        processingTickets: "Procesando gastos...",
        
        // === MENSAJES DE ÉXITO ===
        expenseAdded: "Gasto añadido correctamente",
        expenseUpdated: "Gasto actualizado correctamente",
        expenseDeleted: "Gasto eliminado correctamente",
        groupDeleted: "Grupo eliminado correctamente",
        allFiltersRemoved: "Todos los filtros eliminados",
        filtersRemoved: "Filtros eliminados",
        langChanged: "Idioma cambiado correctamente",
        
        // === MENSAJES DE ERROR ===
        connectionError: "Error de conexión",
        errorUnknown: "Error desconocido",
        langError: "Error al cambiar idioma",
        noProcessedTickets: "No hay gastos procesados para guardar",
        cantDeleteTickets: "No se pudieron eliminar los gastos",
        cantConfirmTickets: "No se pudieron confirmer los gastos",
        errorAddingTrip: "Error al añadir el viaje",
        errorAddingExpense: "Error al añadir el gasto esperado",
        errorProcessingImage: "Error al procesar imagen",
        
        // === MENSAJES DE ESTADO VACÍO ===
        noData: "No hay datos disponibles",
        noTicketsPeriod: "Sin tickets en este período",
        noTicketsMatch: "No hay tickets que coincidan con las fechas seleccionadas",
        noTripsYet: "Sin viajes aún",
        noTripsYetTitle: "Sin viajes aún",
        noTripsYetDescription: "Utiliza el formulario de arriba para crear tu primer viaje",
        noExpectedExpenses: "Sin gastos esperados aún",
        noExpectedExpensesYet: "Sin gastos esperados aún",
        noExpectedExpensesYetDescription: "Utiliza el formulario de arriba para añadir gastos esperados para este viaje",
        noExpectedExpensesText: "Sin gastos esperados aún",
        useFormAbove: "Utiliza el formulario de arriba para añadir gastos esperados para este viaje",
        createFirstTrip: "Utiliza el formulario de arriba para crear tu primer viaje",
        createFirstTripText: "Utiliza el formulario de arriba para crear tu primer viaje",
        useFormAboveText: "Utiliza el formulario de arriba para añadir gastos esperados para este viaje",
        groupsManagementDescriptionText: "Organiza tus gastos en grupos personalizados",
        
        // === VIAJES Y CUADRES ===
        trips: "Viajes",
        tripDetails: "Detalles del Viaje",
        totalAmount: "Importe Total",
        pendingAmount: "Importe Pendiente",
        squareExpense: "Cuadrar Gasto",
        unsquareExpense: "Descuadrar Gasto",
        searchSquare: "Buscar cuadre automático",
        noTrip: "Sin viaje",
        noDescription: "Sin descripción",
        noDetail: "Sin detalle",
        
        // === EXPORTACIÓN ===
        exportPDF: "Exportar PDF",
        exportExcel: "Exportar Excel",
        exportImages: "Exportar Imágenes",
        exportAll: "Exportar Todo",
        
        // === FILTROS ===
        filterByDate: "Filtrar por Fecha",
        filterByUser: "Filtrar por Usuario",
        filterByTrip: "Filtrar por Viaje",
        fromDate: "Desde",
        toDate: "Hasta",
        applyFilters: "Aplicar Filtros",
        clearFilters: "Limpiar Filtros",
        allGroups: "Todos los grupos",
        allUsers: "Todos los usuarios",
        searchGroup: "Buscar grupo...",
        searchUser: "Buscar usuario...",
        
        // === SELECTORES ===
        selectConcept: "Seleccionar concepto...",
        selectUser: "Selecciona un usuario",
        selectGroup: "Selecciona un grupo",
        selectCurrency: "Selecciona moneda",
        selectTrip: "Seleccionar viaje...",
        describeTicket: "Describe el ticket...",
        
        // === ESTADOS DE GRUPOS ===
        allGroupsBalanced: "Todos los grupos están cuadrados",
        noGroupsPending: "No hay grupos con detalles pendientes de cuadrar",
        
        // === CONFIRMACIONES ===
        confirmDelete: "¿Estás seguro de que quieres eliminar este elemento?",
        deleteTicketBatch: "¿Eliminar este ticket del lote?",
        
        // === COLUMNAS DE TABLA ===
        fecha: "Fecha",
        concepto: "Concepto",
        motivo: "Motivo",
        descripcion: "Descripción",
        importeEur: "Importe EUR",
        importeOtraMoneda: "Importe Otra Moneda",
        moneda: "Moneda",
        checkeado: "Checkeado",
        usuario: "Usuario",
        
        // === ERRORES DEL SISTEMA ===
        datesRequired: "Fechas requeridas",
        noImagesInRange: "No hay imágenes en el rango seleccionado",
        noExpensesInRange: "No se encontraron gastos en el rango de fechas especificado",
        sessionExpired: "Sesión expirada, redirigiendo a login",
        
        // === PROCESAMIENTO ===
        preparingProcessing: "Preparando procesamiento...",
        processingTicketsText: "Procesando tickets...",
        
        // === TÍTULOS DE ARCHIVO ===
        gastosTitle: "Gastos",
        
        // === PLACEHOLDERS ===
        allGroupsPlaceholder: "Todos los grupos",
        allUsersPlaceholder: "Todos los usuarios",
        allSelected: "Todos seleccionados"
    },
    
    fr: {
        // === TÍTULOS Y HEADERS ===
        pageTitle: "💳 Gestion des Dépenses",
        headerTitle: "Gestion des Dépenses",
        sidebarUserRole: "Utilisateur",
        sidebarAdminRole: "Administrateur",
        sidebarPrincipal: "Principal",
        sidebarGestion: "Gestion",
        sidebarLogout: "Déconnexion",
        
        // === DESCRIPCIONES PRINCIPALES ===
        mainDescription: "Ajoutez et gérez vos dépenses",
        addTicketDescription: "Ajoutez une dépense individuelle avec photo et extraction automatique",
        multipleTicketsDescription: "Traitez plusieurs tickets à la fois avec vérification intelligente",
        manageGroupsDescription: "Organisez et gérez vos groupes de dépenses",
        groupsManagementDescription: "Organisez vos dépenses en groupes personnalisés",
        selectDateRange: "Sélectionnez la plage de dates pour filtrer vos dépenses",
        dashboardDescription: "Visualisez et confirmez vos dépenses",
        dashboardDateFilterDescription: "Sélectionnez la plage de dates pour le tableau de bord",
        
        // === FORMULARIOS Y CAMPOS ===
        date: "Date",
        concept: "Concept",
        reason: "Motif",
        description: "Description",
        amount: "Montant",
        currency: "Devise",
        image: "Image",
        user: "Utilisateur",
        trip: "Voyage",
        
        // === BOTONES PRINCIPALES ===
        addExpense: "Ajouter Dépense",
        addTrip: "Ajouter Voyage",
        addTripDetail: "Ajouter Détail",
        exportData: "Exporter Données",
        settings: "Paramètres",
        save: "Enregistrer",
        cancel: "Annuler",
        edit: "Modifier",
        delete: "Supprimer",
        close: "Fermer",
        confirm: "Confirmer",
        clear: "Effacer",
        
        // === CONCEPTOS ===
        restaurant: "Restaurant",
        transport: "Transport",
        accommodation: "Hébergement",
        fuel: "Carburant",
        shopping: "Achats",
        entertainment: "Divertissement",
        health: "Santé",
        education: "Éducation",
        technology: "Technologie",
        others: "Autres",
        
        // === ESTADOS Y VALORES ===
        checked: "Vérifié",
        unchecked: "Non vérifié",
        squared: "Équilibré",
        notSquared: "Non équilibré",
        active: "Actif",
        inactive: "Inactif",
        yes: "Oui",
        no: "Non",
        all: "Tous",
        
        // === MENSAJES DEL SISTEMA ===
        success: "Succès",
        error: "Erreur",
        warning: "Avertissement",
        info: "Information",
        loading: "Chargement...",
        saving: "Enregistrement...",
        deleting: "Suppression...",
        processing: "Traitement",
        processingTickets: "Traitement des dépenses...",
        
        // === MENSAJES DE ÉXITO ===
        expenseAdded: "Dépense ajoutée correctement",
        expenseUpdated: "Dépense mise à jour correctement",
        expenseDeleted: "Dépense supprimée correctement",
        groupDeleted: "Groupe supprimé correctement",
        allFiltersRemoved: "Tous les filtres supprimés",
        filtersRemoved: "Filtres supprimés",
        langChanged: "Langue changée avec succès",
        
        // === MENSAJES DE ERROR ===
        connectionError: "Erreur de connexion",
        errorUnknown: "Erreur inconnue",
        langError: "Erreur lors du changement de langue",
        noProcessedTickets: "Aucune dépense traitée à enregistrer",
        cantDeleteTickets: "Impossible de supprimer les dépenses",
        cantConfirmTickets: "Impossible de confirmer les dépenses",
        errorAddingTrip: "Erreur lors de l'ajout du voyage",
        errorAddingExpense: "Erreur lors de l'ajout de la dépense prévue",
        errorProcessingImage: "Erreur lors du traitement de l'image",
        
        // === MENSAJES DE ESTADO VACÍO ===
        noData: "Aucune donnée disponible",
        noTicketsPeriod: "Aucun ticket dans cette période",
        noTicketsMatch: "Aucun ticket ne correspond aux dates sélectionnées",
        noTripsYet: "Aucun voyage encore",
        noTripsYetTitle: "Aucun voyage encore",
        noTripsYetDescription: "Utilisez le formulaire ci-dessus pour créer votre premier voyage",
        noExpectedExpenses: "Aucune dépense prévue encore",
        noExpectedExpensesYet: "Aucune dépense prévue encore",
        noExpectedExpensesYetDescription: "Utilisez le formulaire ci-dessus pour ajouter des dépenses prévues pour ce voyage",
        noExpectedExpensesText: "Aucune dépense prévue encore",
        useFormAbove: "Utilisez le formulaire ci-dessus pour ajouter des dépenses prévues pour ce voyage",
        createFirstTrip: "Utilisez le formulaire ci-dessus pour créer votre premier voyage",
        createFirstTripText: "Utilisez le formulaire ci-dessus pour créer votre premier voyage",
        useFormAboveText: "Utilisez le formulaire ci-dessus pour ajouter des dépenses prévues pour ce voyage",
        groupsManagementDescriptionText: "Organisez vos dépenses en groupes personnalisés",
        
        // === VIAJES Y CUADRES ===
        trips: "Voyages",
        tripDetails: "Détails du Voyage",
        totalAmount: "Montant Total",
        pendingAmount: "Montant en Attente",
        squareExpense: "Équilibrer Dépense",
        unsquareExpense: "Déséquilibrer Dépense",
        searchSquare: "Rechercher équilibrage automatique",
        noTrip: "Sans voyage",
        noDescription: "Sans description",
        noDetail: "Sans détail",
        
        // === EXPORTACIÓN ===
        exportPDF: "Exporter PDF",
        exportExcel: "Exporter Excel",
        exportImages: "Exporter Images",
        exportAll: "Tout Exporter",
        
        // === FILTROS ===
        filterByDate: "Filtrer par Date",
        filterByUser: "Filtrer par Utilisateur",
        filterByTrip: "Filtrer par Voyage",
        fromDate: "Du",
        toDate: "Au",
        applyFilters: "Appliquer Filtres",
        clearFilters: "Effacer Filtres",
        allGroups: "Tous les groupes",
        allUsers: "Tous les utilisateurs",
        searchGroup: "Rechercher groupe...",
        searchUser: "Rechercher utilisateur...",
        
        // === SELECTORES ===
        selectConcept: "Sélectionner un concept",
        selectUser: "Sélectionner un utilisateur",
        selectGroup: "Sélectionner un groupe",
        selectCurrency: "Sélectionner une devise",
        selectTrip: "Sélectionner un voyage",
        describeTicket: "Décrivez le ticket...",
        
        // === ESTADOS DE GRUPOS ===
        allGroupsBalanced: "Tous les groupes sont équilibrés",
        noGroupsPending: "Aucun groupe avec des détails en attente",
        
        // === CONFIRMACIONES ===
        confirmDelete: "Êtes-vous sûr de vouloir supprimer cet élément?",
        deleteTicketBatch: "Supprimer ce ticket du lot?",
        
        // === COLUMNAS DE TABLA ===
        fecha: "Date",
        concepto: "Concept",
        motivo: "Motif",
        descripcion: "Description",
        importeEur: "Montant EUR",
        importeOtraMoneda: "Montant Autre Devise",
        moneda: "Devise",
        checkeado: "Vérifié",
        usuario: "Utilisateur",
        
        // === ERRORES DEL SISTEMA ===
        datesRequired: "Dates requises",
        noImagesInRange: "Aucune image dans la plage sélectionnée",
        noExpensesInRange: "Aucune dépense trouvée dans la plage de dates spécifiée",
        sessionExpired: "Session expirée, redirection vers la connexion",
        
        // === PROCESAMIENTO ===
        preparingProcessing: "Préparation du traitement...",
        processingTicketsText: "Traitement des tickets...",
        
        // === TÍTULOS DE ARCHIVO ===
        gastosTitle: "Dépenses",
        
        // === PLACEHOLDERS ===
        allGroupsPlaceholder: "Tous les groupes",
        allUsersPlaceholder: "Tous les utilisateurs",
        allSelected: "Tous sélectionnés"
    }
};

// Función para obtener traducción
function t(key) {
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    return translations[currentLang]?.[key] || key;
}

// Función para aplicar traducciones dinámicas
function applyDynamicTranslations() {
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    const t = translations[currentLang];
    
    // Aplicar traducciones a elementos con data-translate
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (t[key]) {
            element.textContent = t[key];
        }
    });
    
    // Aplicar traducciones específicas por ID
    const elementsToTranslate = [
        'pageTitle', 'headerTitle', 'sidebarUserRole', 'sidebarAdminRole',
        'sidebarPrincipal', 'sidebarGestion', 'sidebarLogout',
        'mainDescription', 'addTicketDescription', 'multipleTicketsDescription',
        'manageGroupsDescription', 'groupsManagementDescription',
        'selectDateRange', 'dashboardDescription', 'dashboardDateFilterDescription'
    ];
    
    elementsToTranslate.forEach(id => {
        const element = document.getElementById(id);
        if (element && t[id]) {
            element.textContent = t[id];
        }
    });
}

// Inicializar traducciones al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    applyDynamicTranslations();
});