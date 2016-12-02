const Group = React.createClass({
    url: function(){
        return Urls.group_show(this.props.slug);
    },
    render: function(){
        return <li><a href={this.url()}>
            {this.props.slug}: <strong>{this.props.name}</strong>
        </a></li>;
    }
});

const Category = React.createClass({
    url: function(){
        return Urls.category_show(this.props.id);
    },
    render: function(){
        var children = this.props.children.map(function(cat){
            return <Category key={"cat"+cat.id} {...cat}/>;
        });
        var groups = this.props.groups.map(function(group){
            return <Group key={"group"+group.id} {...group}/>;
        });
        var contents = "";
        if (children.length > 0 || groups.length > 0){
            contents = <ul className="dropdown">
                {children}
                <li className="divider"></li>
                {groups}
            </ul>;
        }
        return <li className="has-dropdown">
            <a href={this.url()}>{this.props.name}</a>
            {contents}
        </li>;
    }
});

$(document).ready(function(){
    $.get(Urls.group_tree(), function(data){
        ReactDOM.render(<Category {...data[0]}/>,
                        document.getElementById('group-tree-menu')
        );
        $(document).foundation('topbar', 'reflow');
    });
});