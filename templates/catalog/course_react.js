/* http://stackoverflow.com/questions/728360/most-elegant-way-to-clone-a-javascript-object */
const clone = function(obj) {
    var copy;

    // Handle the 3 simple types, and null or undefined
    if (null == obj || "object" != typeof obj) return obj;

    // Handle Date
    if (obj instanceof Date) {
        copy = new Date();
        copy.setTime(obj.getTime());
        return copy;
    }

    // Handle Array
    if (obj instanceof Array) {
        copy = [];
        for (var i = 0, len = obj.length; i < len; i++) {
            copy[i] = clone(obj[i]);
        }
        return copy;
    }

    // Handle Object
    if (obj instanceof Object) {
        copy = {};
        for (var attr in obj) {
            if (obj.hasOwnProperty(attr)) copy[attr] = clone(obj[attr]);
        }
        return copy;
    }

    throw new Error("Unable to copy obj! Its type isn't supported.");
}

const Tag = React.createClass({
    id: function(){return this.props.id;},
    name: function(){return this.props.name;},
    color: function(){return this.props.color;},
    clicked: function(){
        if (this.props.onClick){
            this.props.onClick(this);
        }
    },
    render: function(){
        var style;
        var klass = "radius label tag-item";
        if (this.props.active){
            klass += " active";
            style = {
                color: this.color(),
                backgroundColor: 'white',
                border: 'solid 2px ' + this.color()
            };
        } else {
            style = {
                backgroundColor: this.color(),
                border: 'solid 2px ' + this.color()
            };
        }
        return <span><a onClick={this.clicked} href="#"
                        style={style} className={klass}>
            {this.name()}
        </a> </span>;
    }
});

const Document = React.createClass({
    ready: function(){return (this.props.state == 'DONE');},
    editable: function(){return this.props.has_perm;},
    date: function(){return moment(this.props.date).format("D MMMM YYYY");},
    edit_url: function(){
        return "{% url 'document_edit' 4242424242 %}"
                             .replace('4242424242', this.props.id);
    },
    url: function(){
        return "{% url 'document_show' 4242424242 %}"
                             .replace('4242424242', this.props.id);
    },
    icon: function(){
        if (this.props.state == 'DONE'){
            return <a href={this.url()}>
                <i className="fi-page-copy round-icon big"></i>
            </a>;
        }
        return <i className="fi-loop round-icon big"></i>;
    },
    edit_icon: function(){
        if (this.ready() && this.editable()){
            return <a href={this.edit_url()}>
                <i className="fi-pencil dark-grey"></i>
            </a>;
        }
        return '';
    },
    description: function(){
        var text = markdown.toHTML(this.props.description);
        if (text != ''){
            var wrap = {__html: text};
            return <p dangerouslySetInnerHTML={wrap} />;
        }
        return '';
    },
    title: function(){
        if (this.ready()){
            return <a href={this.url()}>{this.props.name}</a>; 
        }
        return this.props.name;
    },
    pages: function(){
        if (! this.ready()){
            return "En cours de traitement";
        }
        else if (this.props.pages == 1){
            return "1 page";
        }
        return this.props.pages + " pages";
    },
    tags: function(){
        return this.props.tags.map(function(tag){
            return <Tag key={"tag"+tag.id} {...tag}/>
        });
    },
    render: function(){
        return <div className="row course-row document">
            {this.icon()}
            <div className="course-row-content">
                <h5>
                    {this.title()} {this.edit_icon()}
                    <small> par {this.props.user.name}</small>
                </h5>
                {this.description()}
                <div className="course-content-last-line">
                    <i className="fi-page-filled"></i> {this.pages()}&nbsp;
                    <i className="fi-clock"></i> Uploadé le {this.date()}&nbsp;
                    <i className="fi-pricetag-multiple"></i> {this.tags()}
                </div>
            </div>
        </div>;
    }
});

const DocumentList = React.createClass({
    getInitialState: function(){return {tag_filter: []};},
    tags_in_documents: function(){
        var res = {};
        this.props.document_set.map(function(doc){
            doc.tags.map(function(t){res[t.id] = t;});
        });
        return clone(Object.keys(res).map(function(k){return res[k];}));
    },
    select_tag: function(tag){
        var t = tag.id();
        var i = this.state.tag_filter.indexOf(t);
        if (i >= 0){
            var before = this.state.tag_filter.slice(0, i);
            var after = this.state.tag_filter.slice(i+1);
            this.setState({tag_filter: before.concat(after)});
        } else {
            this.setState({
                tag_filter: this.state.tag_filter.concat([t])
            });
        }
    },
    documents: function(){
        return this.props.document_set.filter(function(doc){
            var admissible = true;
            var dtags = doc.tags.map(function(tag){return tag.id;});
            this.state.tag_filter.map(function(tag){
                if (dtags.indexOf(tag) < 0){
                    admissible = false;
                }
            });
            return admissible;
        }.bind(this));
    },
    render: function(){
        var docs = this.documents().map(function(doc){
            return <Document key={"doc"+doc.id} {...doc} />;
        });

        var tag_filter = this.tags_in_documents().map(function(tag){
            tag.active = (this.state.tag_filter.indexOf(tag.id) >= 0);
            return <Tag key={"tag"+tag.id} onClick={this.select_tag} {...tag}/>;
        }.bind(this));

        return <div>
            <div className="row">
                <h3>Filtres</h3>
                {tag_filter}
                <hr/>
            </div>
            {docs}
        </div>;
    }
});

$(document).ready(function(){
    $.get('{% url "course-detail" slug=course.slug %}', function(course){
        ReactDOM.render(<DocumentList {...course}/>,
                    document.getElementById('documents'));
    });
});