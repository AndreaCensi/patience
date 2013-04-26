
import yaml
import sys

def main():
    
    data = yaml.load(sys.stdin)
    
    f = sys.stdout
    
    f.write("""
    
<html><head><title>Patience results</title>
    
    <style type="text/css">
    body { font-family: Verdana; } 
    tr.clean { display: none; }

    p, tr.header { font-style: italic; font-family: serif; }
    
    tr { padding: 0; margin: 0; border: 0; }
    tr.header{ border-bottom: solid 1px gray; }
    tr.header td { text-align: center }
/*  td.name { border-right: solid 2px gray; }*/
    td { padding: 0; margin: 0; border: 0; 
        }
    
    span.zero { display: none }
    td.name { font-weight: bold; text-align: left; }
    td.number {  width: 3em; font-family: monospace; text-align: center;}
    
    tr.some_modified .num_modified { background-color: orange; }
    tr.missing  { background-color: red; }
    /* tr.some_untracked .num_untracked { background-color: red; } */
    tr.some_to_push .to_push { background-color: yellow; }
    tr.some_to_merge .to_merge { background-color: #aaf; }
    /* TODO: add simple_merge/push */
    
    </style>

</head>
<body>
    
""")
    
    assert data['command'] == 'status'
    
    d = str(data['date'])[:16]
    ts = """ %s @ %s """ % (data['hostname'], d)
    
    f.write("""<table>
    
        <tr class='header'>
            <td> %s</td>
            <td> M </td>
            <td> ? </td>
            <td> push </td> 
            <td> merge </td>
            <td> notes </td>
        </tr>
    """ % ts)
    for r in data['resources']:
        # if not isinstance(status, patience.action.StatusResult):


        short_path = r.short_path
        status = data['results'][short_path]
        t = """
        <tr class="{tr_class}">
            <td class="name">{name}</td>
            <td class="number num_modified">{num_modified}</td>
            <td class="number num_untracked">{num_untracked}</td>
            <td class="number to_push">{to_push}</td>
            <td class="number to_merge">{to_merge}</td>
            <td class="notes">{notes}</td>
        </tr>
        """

        def wrap(x):
            if x:
                return "<span class='some'>%s</span>" % x
            else:
                return "<span class='zero'>%s</span>" % x
    
        classes = ["resource"]
        
        if isinstance(status, Exception):
            classes.append('exception') 
            invalid = '-'
            s = t.format(name=short_path,
                        num_modified=invalid,
                        num_untracked=invalid,
                        to_push=invalid,
                        to_merge=invalid,
                        tr_class=" ".join(classes),
                        notes='%s' % status)

        else:
            if not status.present:
                classes.append('missing')
            else:
                if status.num_modified:
                    classes.append('some_modified')
                else: 
                    classes.append('not_modified')
            
                if status.num_untracked: 
                    classes.append('some_untracked')
                else: 
                    classes.append('not_untracked')
                
                if status.to_merge: 
                    classes.append('some_to_merge')
                else: 
                    classes.append('not_to_merge')

                if status.to_push: 
                    classes.append('some_to_push')
                else: 
                    classes.append('not_to_push')
            
                if not (status.num_modified or 
                    status.num_untracked or
                    status.to_merge or 
                    status.to_push): 
                    classes.append('clean')

                
            s = t.format(name=short_path,
                        num_modified=wrap(status.num_modified),
                        num_untracked=wrap(status.num_untracked),
                        to_push=wrap(status.to_push),
                        to_merge=wrap(status.to_merge),
                        tr_class=" ".join(classes),
                        notes="")
        
        f.write(s)
        
    f.write('</table>\n')

    f.write("""</body></html>""")
    
if __name__ == '__main__':
    main()
