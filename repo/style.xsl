<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/plugins">

<html>
<head>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous" />
    <title>GBD - QGIS Plugin Repository</title>
</head>
<body>
    <div class="container" style="max-width : 500px">
        <div class="page-header" style="color : #0070B8">
            <h1>QGIS Plugin Repository <small>Geoinformatikbüro Dassau GmbH</small></h1>
        </div>
        <xsl:for-each select="/plugins/pyqgis_plugin">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <h2 class="panel-title">
                        <xsl:value-of select="@name" /> - Version: <xsl:value-of select="@version" />
                    </h2>
                </div>
                <div class="panel-body">
                    <p>
                        <xsl:value-of select="description" />
                    </p>
                    <div class="btn-group pull-right" role="group" aria-label="...">
                        <a class="btn btn-primary">
                            <xsl:attribute name="href">
                                <xsl:value-of select="download_url" />
                            </xsl:attribute>
                            Download
                        </a>
                     </div>
                 </div>
            </div>
        </xsl:for-each>
    </div>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
</body>
</html>

</xsl:template>

</xsl:stylesheet> 
